import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

# Load datasets
orders = pd.read_csv("dataset/sample_-_superstore-Orders.csv")
people = pd.read_csv("dataset/sample_-_superstore-People.csv")
returns = pd.read_csv("dataset/sample_-_superstore-Returns.csv")

# Display first 5 rows
print("ORDERS DATA")
print(orders.head())

print("\nPEOPLE DATA")
print(people.head())

print("\nRETURNS DATA")
print(returns.head())

# Display dataset shapes
print("\nDATASET SHAPES")
print("Orders:", orders.shape)
print("People:", people.shape)
print("Returns:", returns.shape)



# DATA QUALITY INSPECTION

print("\n========== DATA QUALITY CHECK ==========")

# 1. Check column names
print("\nOrders Columns:")
print(orders.columns.tolist())

# 2. Check missing values
print("\nMissing Values:")
print("Orders:\n", orders.isnull().sum())
print("People:\n", people.isnull().sum())
print("Returns:\n", returns.isnull().sum())

# 3. Check duplicate records
print("\nDuplicate Records:")
print("Orders:", orders.duplicated().sum())
print("People:", people.duplicated().sum())
print("Returns:", returns.duplicated().sum())

# 4. Check data types
print("\nData Types:")
print(orders.dtypes)



# DATE CONVERSION

orders["Order Date"] = pd.to_datetime(
    orders["Order Date"], format="%m/%d/%Y"
)

orders["Ship Date"] = pd.to_datetime(
    orders["Ship Date"], format="%m/%d/%Y"
)

print("\n========== DATE CONVERSION ==========")

print(orders[["Order Date", "Ship Date"]].dtypes)

print("\nDate Range:")
print("First Order:", orders["Order Date"].min())
print("Last Order:", orders["Order Date"].max())


# MERGE DATASETS

# Merge Orders with Returns
analysis_df = orders.merge(
    returns,
    on="Order ID",
    how="left",
    validate="many_to_one"
)

# Mark orders without returns as No
analysis_df["Returned"] = analysis_df["Returned"].fillna("No")

# Merge with People
analysis_df = analysis_df.merge(
    people,
    on="Region",
    how="left",
    validate="many_to_one"
)

# Create additional columns
analysis_df["Order Year"] = analysis_df["Order Date"].dt.year
analysis_df["Order Month"] = analysis_df["Order Date"].dt.month

analysis_df["Shipping Days"] = (
    analysis_df["Ship Date"] - analysis_df["Order Date"]
).dt.days

# Display results
print("\n========== MERGED DATASET ==========")

print("Shape:", analysis_df.shape)

print("\nFirst 5 Records:")
print(analysis_df.head())

print("\nReturned Orders:")
print(analysis_df["Returned"].value_counts())

print("\nRegional Managers:")
print(analysis_df[["Region", "Regional Manager"]].drop_duplicates())



# BUSINESS KPI ANALYSIS

total_sales = analysis_df["Sales"].sum()
total_profit = analysis_df["Profit"].sum()
total_quantity = analysis_df["Quantity"].sum()

total_orders = analysis_df["Order ID"].nunique()
total_customers = analysis_df["Customer ID"].nunique()

average_order_value = total_sales / total_orders
profit_margin = (total_profit / total_sales) * 100

returned_orders = returns["Order ID"].nunique()
return_rate = (returned_orders / total_orders) * 100

print("\n========== BUSINESS KPI ANALYSIS ==========")

print(f"Total Sales: ${total_sales:,.2f}")
print(f"Total Profit: ${total_profit:,.2f}")
print(f"Total Quantity Sold: {total_quantity:,}")
print(f"Total Unique Orders: {total_orders:,}")
print(f"Total Unique Customers: {total_customers:,}")
print(f"Average Order Value: ${average_order_value:,.2f}")
print(f"Profit Margin: {profit_margin:.2f}%")
print(f"Unique Returned Orders: {returned_orders:,}")
print(f"Order Return Rate: {return_rate:.2f}%")


# CATEGORY-WISE ANALYSIS

category_analysis = analysis_df.groupby("Category").agg(
    Total_Sales=("Sales", "sum"),
    Total_Profit=("Profit", "sum"),
    Total_Quantity=("Quantity", "sum")
)

category_analysis["Profit_Margin"] = (
    category_analysis["Total_Profit"] /
    category_analysis["Total_Sales"]
) * 100

category_analysis = category_analysis.sort_values(
    by="Total_Sales",
    ascending=False
)

print("\n========== CATEGORY ANALYSIS ==========")
print(category_analysis.round(2))

print("\nBest Sales Category:")
print(category_analysis["Total_Sales"].idxmax())

print("\nBest Profit Category:")
print(category_analysis["Total_Profit"].idxmax())

print("\nLowest Profit Category:")
print(category_analysis["Total_Profit"].idxmin())



# SUB-CATEGORY ANALYSIS

subcategory_analysis = analysis_df.groupby("Sub-Category").agg(
    Total_Sales=("Sales", "sum"),
    Total_Profit=("Profit", "sum"),
    Total_Quantity=("Quantity", "sum")
)

subcategory_analysis = subcategory_analysis.sort_values(
    by="Total_Profit",
    ascending=False
)

print("\n========== SUB-CATEGORY ANALYSIS ==========")

print(subcategory_analysis.round(2))

print("\nTOP 5 PROFITABLE SUB-CATEGORIES:")
print(subcategory_analysis.head(5))

print("\nBOTTOM 5 SUB-CATEGORIES:")
print(subcategory_analysis.tail(5))

print("\nLOSS-MAKING SUB-CATEGORIES:")
print(subcategory_analysis[
    subcategory_analysis["Total_Profit"] < 0
])

# VISUALIZATION 1: PROFIT BY SUB-CATEGORY

plt.figure(figsize=(12, 7))

plot_data = subcategory_analysis.sort_values(
    by="Total_Profit",
    ascending=True
).reset_index()

sns.barplot(
    data=plot_data,
    x="Total_Profit",
    y="Sub-Category"
)

plt.axvline(x=0, color="black", linewidth=1)

plt.title("Profit by Product Sub-Category", fontsize=16)
plt.xlabel("Total Profit ($)")
plt.ylabel("Sub-Category")

plt.tight_layout()

plt.savefig(
    "output/profit_by_subcategory.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

print("Profit chart saved successfully!")
# VISUALIZATION 2: SALES BY CATEGORY

plt.figure(figsize=(9, 6))

category_data = category_analysis.reset_index()

sns.barplot(
    data=category_data,
    x="Category",
    y="Total_Sales"
)

plt.title("Sales by Product Category", fontsize=16)
plt.xlabel("Product Category")
plt.ylabel("Total Sales ($)")

plt.tight_layout()

plt.savefig(
    "output/sales_by_category.png",
    dpi=300,
    bbox_inches="tight"
)

plt.show()

print("Sales by Category chart saved successfully!")

# Sales by Region
plt.figure(figsize=(8, 5))

region_sales = orders.groupby('Region')['Sales'].sum().sort_values(ascending=False)

region_sales.plot(kind='bar', color='skyblue')

plt.title('Total Sales by Region')
plt.xlabel('Region')
plt.ylabel('Total Sales')
plt.xticks(rotation=0)

plt.tight_layout()
plt.savefig('output/sales_by_region.png')
plt.show()



# Monthly Sales Trend

orders['Order Date'] = pd.to_datetime(orders['Order Date'])

orders['Month'] = orders['Order Date'].dt.to_period('M')

monthly_sales = orders.groupby('Month')['Sales'].sum()

plt.figure(figsize=(12, 6))

monthly_sales.plot(kind='line', marker='o')

plt.title('Monthly Sales Trend')
plt.xlabel('Month')
plt.ylabel('Total Sales')
plt.xticks(rotation=45)

plt.grid(True)
plt.tight_layout()

plt.savefig('output/monthly_sales_trend.png')
plt.show()


# Top 10 Products by Sales

top_products = (
    orders.groupby('Product Name')['Sales']
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

plt.figure(figsize=(10, 6))

top_products.sort_values().plot(kind='barh')

plt.title('Top 10 Products by Sales')
plt.xlabel('Total Sales')
plt.ylabel('Product Name')

plt.tight_layout()

plt.savefig('output/top_10_products.png')
plt.show()