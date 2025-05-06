# Global Logistics Tracking Platform (Streamlit Version)

A lightweight, purely Python-based logistics tracking platform. This application simulates a supply chain engine with a dynamic pricing algorithm and an interactive package tracking timeline.

This project was intentionally designed to be **simple** and **100% Python**, removing the complexity of JavaScript/HTML frontends while relying on a robust cloud database backend.

## Features
- **Visual Tracking:** Customers can track their packages using a unique tracking number to see a historical timeline of the package's journey.
- **Dynamic Pricing Engine:** Shipping costs are automatically calculated based on weight and cargo type (Hazardous, Perishable, Electronics, Standard).
- **Admin Hub Panel:** Employees can dynamically update the location and status of packages traversing the supply chain.

## Tech Stack
- **Frontend / Logic:** Python, Streamlit, Pandas
- **Database:** MySQL (Designed for free cloud databases like [TiDB Serverless](https://tidbcloud.com/) or local MySQL)

## Deployment (Free & Easy)

### 1. Setup a Free Cloud Database (TiDB)
1. Go to [TiDB Serverless](https://tidbcloud.com/) and sign up for a free account.
2. Create a free Serverless Cluster.
3. Once created, click "Connect" and select "PyMySQL" or "mysql-connector-python".
4. Copy the host, user, password, and port provided.

### 2. Run Locally
1. Clone this repository.
2. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```
3. Create a `.env` file in the root directory and add your TiDB credentials:
   ```env
   DB_HOST=gateway01.us-east-1.prod.aws.tidbcloud.com
   DB_USER=your_username
   DB_PASSWORD=your_password
   DB_NAME=test
   DB_PORT=4000
   ```
4. Run the application:
   ```bash
   streamlit run app.py
   ```

### 3. Deploy to Streamlit Community Cloud (Free)
1. Push this repository to GitHub.
2. Go to [Streamlit Community Cloud](https://share.streamlit.io/) and log in with GitHub.
3. Click "New app" and point it to your GitHub repository and the `app.py` file.
4. Click "Advanced settings" before deploying and paste your database credentials into the **Secrets** section:
   ```toml
   DB_HOST = "gateway01.us-east-1.prod.aws.tidbcloud.com"
   DB_USER = "your_username"
   DB_PASSWORD = "your_password"
   DB_NAME = "test"
   DB_PORT = "4000"
   ```
5. Click **Deploy!** Your app is now live on the internet connected to a real cloud database.
