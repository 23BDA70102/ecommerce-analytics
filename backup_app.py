from flask import Flask, render_template, request, jsonify, redirect, url_for
import pandas as pd
import numpy as np
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB
ALLOWED_EXTENSIONS = {'csv', 'xlsx'}

# Create uploads folder
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Global variable for data
df = None

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_default_data():
    global df
    try:
        df = pd.read_csv('large_sample_data.csv')
        df['date'] = pd.to_datetime(df['date'])
        print(f"✅ Loaded default data: {len(df)} rows")
    except Exception as e:
        print(f"Error loading default data: {e}")
        # Create sample data
        dates = pd.date_range(start='2024-01-01', end='2024-06-30', freq='D')
        df = pd.DataFrame({
            'date': np.random.choice(dates, 500),
            'product': np.random.choice(['Laptop', 'Phone', 'Shirt', 'Shoes', 'Book'], 500),
            'category': np.random.choice(['Electronics', 'Clothing', 'Books'], 500),
            'quantity': np.random.randint(1, 20, 500),
            'sales': np.random.uniform(100, 5000, 500),
            'region': np.random.choice(['North', 'South', 'East', 'West'], 500)
        })
        print("✅ Created sample data")

# Load default data on startup
load_default_data()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    global df
    
    if request.method == 'POST':
        # Check if file was uploaded
        if 'file' not in request.files:
            return redirect(url_for('upload'))
        
        file = request.files['file']
        
        # Check if file is selected
        if file.filename == '':
            return redirect(url_for('upload'))
        
        # Check if file is allowed
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            # Load the file
            try:
                if filename.endswith('.csv'):
                    df = pd.read_csv(filepath)
                else:
                    df = pd.read_excel(filepath)
                
                if 'date' in df.columns:
                    df['date'] = pd.to_datetime(df['date'])
                
                print(f"✅ Uploaded and loaded: {len(df)} rows")
                return redirect(url_for('analytics'))
                
            except Exception as e:
                print(f"Error loading file: {e}")
                return f"Error loading file: {e}"
    
    # GET request - show upload form
    return render_template('upload.html')

@app.route('/analytics')
def analytics():
    global df
    
    if df is None:
        load_default_data()
    
    total_sales = f"${df['sales'].sum():,.2f}"
    total_orders = f"{len(df):,}"
    avg_order = f"${df['sales'].mean():,.2f}"
    total_quantity = f"{df['quantity'].sum():,}"
    
    categories = ['All'] + sorted(df['category'].unique().tolist())
    regions = ['All'] + sorted(df['region'].unique().tolist())
    
    return render_template('analytics.html', 
                         total_sales=total_sales,
                         total_orders=total_orders,
                         avg_order=avg_order,
                         total_quantity=total_quantity,
                         categories=categories,
                         regions=regions)

@app.route('/api/chart/sales-trend')
def sales_trend():
    global df
    if df is None:
        load_default_data()
    
    # Apply filters
    df_filtered = df.copy()
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    category = request.args.get('category')
    
    if start_date:
        df_filtered = df_filtered[df_filtered['date'] >= pd.to_datetime(start_date)]
    if end_date:
        df_filtered = df_filtered[df_filtered['date'] <= pd.to_datetime(end_date)]
    if category and category != 'All':
        df_filtered = df_filtered[df_filtered['category'] == category]
    
    daily = df_filtered.groupby('date')['sales'].sum().reset_index()
    dates = daily['date'].dt.strftime('%Y-%m-%d').tolist()
    sales = daily['sales'].tolist()
    return jsonify({'dates': dates, 'sales': sales})

@app.route('/api/chart/top-products')
def top_products():
    global df
    if df is None:
        load_default_data()
    
    # Apply filters
    df_filtered = df.copy()
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    category = request.args.get('category')
    
    if start_date:
        df_filtered = df_filtered[df_filtered['date'] >= pd.to_datetime(start_date)]
    if end_date:
        df_filtered = df_filtered[df_filtered['date'] <= pd.to_datetime(end_date)]
    if category and category != 'All':
        df_filtered = df_filtered[df_filtered['category'] == category]
    
    top = df_filtered.groupby('product')['sales'].sum().nlargest(10).reset_index()
    products = top['product'].tolist()
    sales = top['sales'].tolist()
    return jsonify({'products': products, 'sales': sales})

@app.route('/api/chart/category-sales')
def category_sales():
    global df
    if df is None:
        load_default_data()
    
    # Apply filters
    df_filtered = df.copy()
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    category = request.args.get('category')
    
    if start_date:
        df_filtered = df_filtered[df_filtered['date'] >= pd.to_datetime(start_date)]
    if end_date:
        df_filtered = df_filtered[df_filtered['date'] <= pd.to_datetime(end_date)]
    if category and category != 'All':
        df_filtered = df_filtered[df_filtered['category'] == category]
    
    cat = df_filtered.groupby('category')['sales'].sum().reset_index()
    categories = cat['category'].tolist()
    sales = cat['sales'].tolist()
    return jsonify({'categories': categories, 'sales': sales})

@app.route('/api/chart/region-performance')
def region_performance():
    global df
    if df is None:
        load_default_data()
    
    # Apply filters
    df_filtered = df.copy()
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    category = request.args.get('category')
    
    if start_date:
        df_filtered = df_filtered[df_filtered['date'] >= pd.to_datetime(start_date)]
    if end_date:
        df_filtered = df_filtered[df_filtered['date'] <= pd.to_datetime(end_date)]
    if category and category != 'All':
        df_filtered = df_filtered[df_filtered['category'] == category]
    
    reg = df_filtered.groupby('region')['sales'].sum().reset_index()
    regions = reg['region'].tolist()
    sales = reg['sales'].tolist()
    return jsonify({'regions': regions, 'sales': sales})

@app.route('/api/prediction/stats')
def prediction_stats():
    global df
    if df is None:
        load_default_data()
    
    # Apply filters
    df_filtered = df.copy()
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    category = request.args.get('category')
    
    if start_date:
        df_filtered = df_filtered[df_filtered['date'] >= pd.to_datetime(start_date)]
    if end_date:
        df_filtered = df_filtered[df_filtered['date'] <= pd.to_datetime(end_date)]
    if category and category != 'All':
        df_filtered = df_filtered[df_filtered['category'] == category]
    
    monthly = df_filtered.groupby(df_filtered['date'].dt.to_period('M'))['sales'].sum()
    if len(monthly) > 1:
        growth = ((monthly.iloc[-1] - monthly.iloc[-2]) / monthly.iloc[-2]) * 100
        avg = monthly.mean()
        forecast = monthly.iloc[-1] * (1 + growth/100)
        return jsonify({
            'growth_rate': f'{growth:.1f}%',
            'avg_monthly': f'${avg:,.2f}',
            'next_month_forecast': f'${forecast:,.2f}'
        })
    return jsonify({'growth_rate': 'N/A', 'avg_monthly': 'N/A', 'next_month_forecast': 'N/A'})

@app.route('/data')
def data():
    global df
    if df is None:
        load_default_data()
    
    return render_template('data_table.html', 
                         table=df.head(50).to_html(classes='table table-striped'),
                         total_rows=len(df))

if __name__ == '__main__':
    print("\n" + "="*60)
    print("✅ SERVER RUNNING SUCCESSFULLY!")
    print("📍 Home: http://localhost:5001")
    print("📊 Analytics: http://localhost:5001/analytics")
    print("📤 Upload: http://localhost:5001/upload")
    print("="*60 + "\n")
    app.run(debug=True, port=5001)