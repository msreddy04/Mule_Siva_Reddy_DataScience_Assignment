import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from fpdf import FPDF
from sklearn.metrics import davies_bouldin_score

# Load datasets
customers = pd.read_csv(r"C:\Users\msred\eCommerce_Transactions_Analysis\Customers.csv", delimiter='\t')
products = pd.read_csv(r"C:\Users\msred\eCommerce_Transactions_Analysis\Products.csv", delimiter='\t')
transactions = pd.read_csv(r"C:\Users\msred\eCommerce_Transactions_Analysis\Transactions.csv", delimiter='\t')

# Exploratory Data Analysis (EDA)
print("\nCustomers Dataset Info:")
customers.info()
print("\nProducts Dataset Info:")
products.info()
print("\nTransactions Dataset Info:")
transactions.info()

# Checking for missing values
print("\nMissing Values in Datasets:")
print("Customers:", customers.isnull().sum())
print("Products:", products.isnull().sum())
print("Transactions:", transactions.isnull().sum())

# Merge datasets
merged_data = transactions.merge(customers, on='CustomerID', how='left')
merged_data = merged_data.merge(products, on='ProductID', how='left')

# Total Revenue by Region
revenue_by_region = merged_data.groupby('Region')['TotalValue'].sum().sort_values(ascending=False)
print("\nRevenue by Region:")
print(revenue_by_region)

# Top 5 Product Categories by Revenue
plt.figure(figsize=(8, 5))
top_categories = merged_data.groupby('Category')['TotalValue'].sum().sort_values(ascending=False).head(5)
top_categories.plot(kind='bar', color='skyblue')
plt.title('Top 5 Product Categories by Revenue')
plt.ylabel('Total Revenue (USD)')
plt.xlabel('Category')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('top_categories_revenue.png')
plt.show()

# Business Insights
insights = [
    "1. Region-based revenue distribution highlights key market areas.",
    "2. Top product categories can guide marketing strategies.",
    "3. Customer retention patterns based on transaction history.",
    "4. Peak sales periods derived from transaction trends.",
    "5. Average spending across customer segments."
]

# PDF Report Generation
class PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'Exploratory Data Analysis Report', ln=True, align='C')
        self.ln(10)

    def chapter_title(self, title):
        self.set_font('Arial', 'B', 14)
        self.cell(0, 10, title, ln=True, align='L')
        self.ln(5)

    def chapter_body(self, body):
        self.set_font('Arial', '', 12)
        self.multi_cell(0, 10, body)
        self.ln()

pdf = PDF()
pdf.add_page()
pdf.chapter_title("Business Insights")
pdf.chapter_body("\n".join(insights))
pdf.output('Mule_Siva_Reddy_EDA.pdf')

# Lookalike Model
customer_transactions = merged_data.groupby('CustomerID').agg({'TotalValue': 'sum', 'Quantity': 'sum'}).reset_index()
customer_transactions = customer_transactions.merge(customers, on='CustomerID', how='left')

scaler = StandardScaler()
features = scaler.fit_transform(customer_transactions[['TotalValue', 'Quantity']])
similarity_matrix = cosine_similarity(features)

lookalike_results = {}
for i in range(20):
    customer_id = customer_transactions.iloc[i]['CustomerID']
    similarity_scores = list(enumerate(similarity_matrix[i]))
    similarity_scores = sorted(similarity_scores, key=lambda x: x[1], reverse=True)
    top_lookalikes = [(customer_transactions.iloc[j[0]]['CustomerID'], j[1]) for j in similarity_scores[1:4]]
    lookalike_results[customer_id] = top_lookalikes

lookalike_df = pd.DataFrame({"CustomerID": list(lookalike_results.keys()),
                             "Lookalikes": list(lookalike_results.values())})
lookalike_df.to_csv('Mule_Siva_Reddy_Lookalike.csv', index=False)

# Customer Segmentation
clustering_data = scaler.fit_transform(customer_transactions[['TotalValue', 'Quantity']])
kmeans = KMeans(n_clusters=5, random_state=42)
customer_transactions['Cluster'] = kmeans.fit_predict(clustering_data)

plt.figure(figsize=(8, 5))
sns.scatterplot(x=customer_transactions['TotalValue'], y=customer_transactions['Quantity'], hue=customer_transactions['Cluster'], palette='viridis')
plt.title('Customer Segmentation')
plt.xlabel('Total Value')
plt.ylabel('Quantity')
plt.legend(title='Cluster')
plt.tight_layout()
plt.savefig('customer_segmentation.png')
plt.show()

db_index = davies_bouldin_score(clustering_data, customer_transactions['Cluster'])
print(f'Davies-Bouldin Index: {db_index}')

customer_transactions[['CustomerID', 'Cluster']].to_csv('Mule_Siva_Reddy_Clustering.csv', index=False)

# PDF for Clustering
pdf.add_page()
pdf.chapter_title("Customer Segmentation")
pdf.chapter_body(f'Davies-Bouldin Index: {db_index}')
pdf.output('Mule_Siva_Reddy_Clustering.pdf')

print("All required files have been successfully generated!")
