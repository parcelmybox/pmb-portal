-- Create the database
CREATE DATABASE IF NOT EXISTS pmb_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Create the user and grant privileges
CREATE USER IF NOT EXISTS 'pmb_user'@'localhost' IDENTIFIED BY 'pmb_user';
GRANT ALL PRIVILEGES ON pmb_db.* TO 'pmb_user'@'localhost';
FLUSH PRIVILEGES;
