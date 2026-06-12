import pandas as pd
import numpy as np

n = 10000

df = pd.DataFrame({
    "date": pd.date_range("2024-01-01", periods=n),
    "product": np.random.choice(
        ["Laptop","Phone","TV","Tablet","Headphones"],
        n
    ),
    "category": np.random.choice(
        ["Electronics","Fashion","Books","Home"],
        n
    ),
    "quantity": np.random.randint(1,20,n),
    "sales": np.random.randint(100,10000,n),
    "region": np.random.choice(
        ["North","South","East","West"],
        n
    )
})

df.to_csv("large_sales_data.csv", index=False)

print("CSV Created Successfully!")