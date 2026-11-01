-- ========================================================================
-- Bespoke Tailoring Measurement & Fabric-Yardage Calculator
-- Production MySQL Database Schema DDL
-- Compatible with MySQL 8.0+ / MariaDB 10.5+
-- ========================================================================

CREATE DATABASE IF NOT EXISTS `bespoke_tailordb` 
  CHARACTER SET utf8mb4 
  COLLATE utf8mb4_unicode_ci;

USE `bespoke_tailordb`;

-- 1. Customers Table (Grahak Diary)
CREATE TABLE IF NOT EXISTS `customers` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(120) NOT NULL COMMENT 'Customer Full Name',
  `phone` VARCHAR(30) NULL COMMENT 'Primary WhatsApp/Phone',
  `email` VARCHAR(120) NULL COMMENT 'Contact Email',
  `city` VARCHAR(80) NULL DEFAULT 'Mumbai' COMMENT 'Location / Area',
  `notes` TEXT NULL COMMENT 'Special anatomical or preference notes',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  INDEX `idx_customer_name` (`name`),
  INDEX `idx_customer_phone` (`phone`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Measurements Table (Naap Docket)
CREATE TABLE IF NOT EXISTS `measurements` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `customer_id` INT NOT NULL,
  `unit` VARCHAR(10) NOT NULL DEFAULT 'in' COMMENT 'Unit of measure: in or cm',
  
  -- Upper Body Dimensions (Inches)
  `neck` DECIMAL(5,2) DEFAULT 16.50 COMMENT 'Gala circumference',
  `shoulder` DECIMAL(5,2) DEFAULT 18.20 COMMENT 'Kandha width',
  `chest` DECIMAL(5,2) DEFAULT 41.50 COMMENT 'Chhati circumference',
  `bicep` DECIMAL(5,2) DEFAULT 14.00 COMMENT 'Aasteen bicep circumference',
  `wrist` DECIMAL(5,2) DEFAULT 7.50 COMMENT 'Mori / wrist circumference',
  `sleeve_length` DECIMAL(5,2) DEFAULT 25.00 COMMENT 'Aasteen length',
  `jacket_length` DECIMAL(5,2) DEFAULT 30.00 COMMENT 'Koti / Jacket length',
  `shirt_length` DECIMAL(5,2) DEFAULT 29.50 COMMENT 'Kurta / Shirt length',

  -- Lower Body Dimensions (Inches)
  `waist` DECIMAL(5,2) DEFAULT 34.00 COMMENT 'Kamar circumference',
  `hip` DECIMAL(5,2) DEFAULT 40.00 COMMENT 'Seat / Hip basin circumference',
  `inseam` DECIMAL(5,2) DEFAULT 32.50 COMMENT 'Lambai inside leg',
  `outseam` DECIMAL(5,2) DEFAULT 41.00 COMMENT 'Trouser outseam length',
  `thigh` DECIMAL(5,2) DEFAULT 24.00 COMMENT 'Thigh circumference (Jhaang)',
  `calf` DECIMAL(5,2) DEFAULT 15.50 COMMENT 'Calf circumference (Pindli)',

  -- Fit Preferences & Masterji Posture Observations
  `ease_preset` VARCHAR(20) NOT NULL DEFAULT 'barabar' COMMENT 'chust (slim), barabar (regular), dhila (loose)',
  `posture_notes` TEXT NULL COMMENT 'E.g., right shoulder drop, prominent abdomen, erect stance',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT `fk_measurements_customer`
    FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  INDEX `idx_measurements_customer` (`customer_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Orders Table (Katai Parchi & Commercial Docket)
CREATE TABLE IF NOT EXISTS `orders` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `order_no` VARCHAR(40) NOT NULL UNIQUE COMMENT 'Unique Atelier Order Number e.g. BY-2024-89',
  `customer_id` INT NOT NULL,
  `measurement_id` INT NULL,

  -- Garment & Textile Specifications
  `garment_style` VARCHAR(80) NOT NULL COMMENT 'E.g. Bandhgala, 2-Piece Suit, Jodhpuri, Kurta Pajama',
  `fabric_name` VARCHAR(150) NULL COMMENT 'E.g. Raymond Super 120s Charcoal',
  `fabric_mill` VARCHAR(100) NULL COMMENT 'E.g. Raymond Savile Collection India',
  `fabric_width_in` DECIMAL(5,2) NOT NULL DEFAULT 58.00 COMMENT 'Bolt Width (Pana/Arz) in inches: 36, 44, 54, 58',
  `fabric_pattern` VARCHAR(30) NOT NULL DEFAULT 'plain' COMMENT 'plain, stripe, plaid, directional',
  `fabric_image_url` VARCHAR(255) NULL COMMENT 'Fabric swatch preview image',

  -- Yardage Calculations (Exact Python Output)
  `total_meters` DECIMAL(5,2) NOT NULL COMMENT 'Kul Kapda in meters',
  `total_yards` DECIMAL(5,2) NOT NULL COMMENT 'Yardage equivalent',
  `total_gaj` DECIMAL(5,2) NOT NULL COMMENT 'Gaj (Gaz) equivalent in Indian textile measure',
  `jacket_meters` DECIMAL(5,2) DEFAULT 0.00 COMMENT 'Jacket requirement',
  `trouser_meters` DECIMAL(5,2) DEFAULT 0.00 COMMENT 'Trouser requirement',
  `lining_meters` DECIMAL(5,2) DEFAULT 0.00 COMMENT 'Astar silk/twill lining requirement',
  `canvas_meters` DECIMAL(5,2) DEFAULT 0.00 COMMENT 'Bukram / Horsehair canvas requirement',

  -- Commercials & Billing (INR)
  `fabric_cost` DECIMAL(10,2) DEFAULT 0.00 COMMENT 'Cloth price',
  `stitching_cost` DECIMAL(10,2) DEFAULT 0.00 COMMENT 'Karigari stitching charges',
  `total_bill` DECIMAL(10,2) DEFAULT 0.00 COMMENT 'Total bill payable',
  `advance_paid` DECIMAL(10,2) DEFAULT 0.00 COMMENT 'Advance deposit received',
  `balance_amount` DECIMAL(10,2) DEFAULT 0.00 COMMENT 'Outstanding payment',

  -- Workshop & Fitting Stage
  `status` VARCHAR(40) NOT NULL DEFAULT 'Trial Scheduled' COMMENT 'Draft, Measured, Cutting, Trial Scheduled, Ready, Delivered',
  `trial_stage` VARCHAR(30) DEFAULT 'Trial #1' COMMENT 'Basting, Trial #1, Trial #2, Final',
  `trial_date` VARCHAR(40) NULL COMMENT 'Trial Date description',
  `delivery_date` VARCHAR(40) NULL COMMENT 'Final Delivery Date description',
  `senior_cutter` VARCHAR(100) DEFAULT 'Master V. Sharma',
  `workshop_section` VARCHAR(100) DEFAULT 'Marine Lines Workshop',
  `notes` TEXT NULL,

  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `updated_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  CONSTRAINT `fk_orders_customer`
    FOREIGN KEY (`customer_id`) REFERENCES `customers` (`id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_orders_measurement`
    FOREIGN KEY (`measurement_id`) REFERENCES `measurements` (`id`)
    ON DELETE SET NULL
    ON UPDATE CASCADE,
  INDEX `idx_orders_customer` (`customer_id`),
  INDEX `idx_orders_status` (`status`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

