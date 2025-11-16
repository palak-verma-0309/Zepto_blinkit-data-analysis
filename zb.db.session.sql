--Total Orders & Total Revenue--
SELECT 
COUNT(*) AS total_orders,
SUM(TotalAmount) AS total_revenue
FROM grocery_orders;

--Brand-wise Revenue & Orders--
SELECT 
    Brand,
    COUNT(*) AS total_orders,
    SUM(TotalAmount) AS total_revenue,
    ROUND(AVG('DeliveryTime(min)'),2) AS avg_delivery_time,
    ROUND(AVG(Rating),2) AS avg_rating
FROM grocery_orders
GROUP BY Brand;

-- City-wise Order Ranking --
SELECT 
    City,
    COUNT(*) AS total_orders,
    SUM(TotalAmount) AS revenue
FROM grocery_orders
GROUP BY City
ORDER BY total_orders DESC;

-- Category-wise Quantity Sold --
SELECT 
    Category,
    SUM(Quantity) AS total_units_sold,
    SUM(TotalAmount) AS revenue
FROM grocery_orders
GROUP BY Category
ORDER BY total_units_sold DESC;

-- Monthly Sales Trend --
SELECT 
    OrderMonth,
    COUNT(*) AS orders,
    SUM(TotalAmount) AS revenue
FROM grocery_orders
GROUP BY OrderMonth
ORDER BY orders DESC;

-- Weekday Trend Analysis --
SELECT 
    OrderWeekday,
    COUNT(*) AS total_orders,
    SUM(TotalAmount) AS revenue
FROM grocery_orders
GROUP BY OrderWeekday
ORDER BY total_orders DESC;

-- Top Selling Products --
SELECT 
    Product,
    SUM(Quantity) AS total_units,
    SUM(TotalAmount) AS revenue
FROM grocery_orders
GROUP BY Product
ORDER BY total_units DESC
LIMIT 10;

--Fast vs Slow Delivery Rating Comparison--
SELECT 
    DeliverySpeed,
    COUNT(*) AS total_orders,
    ROUND(AVG(Rating),2) AS avg_rating
FROM grocery_orders
GROUP BY DeliverySpeed;

-- Rating Distribution --
SELECT 
    Rating,
    COUNT(*) AS total_orders
FROM grocery_orders
GROUP BY Rating
ORDER BY Rating;

--Payment method analysis--
SELECT 
    PaymentMode,
    COUNT(*) AS order_count,
    SUM(TotalAmount) AS revenue
FROM grocery_orders
GROUP BY PaymentMode
ORDER BY order_count DESC;

-- Window Function — Revenue Rank by City
SELECT 
    City,
    SUM(TotalAmount) AS revenue,
    RANK() OVER(ORDER BY SUM(TotalAmount) DESC) AS city_rank
FROM grocery_orders
GROUP BY City;

-- Overall KPI Summary Statistics --
SELECT 
    COUNT(*) AS total_orders,
    SUM(TotalAmount) AS total_revenue,
    ROUND(AVG('DeliveryTime(min)'),2) AS avg_delivery_time,
    ROUND(AVG(Rating),2) AS avg_rating,
    COUNT(DISTINCT City) AS cities_served,
    COUNT(DISTINCT Product) AS unique_products
FROM grocery_orders;







