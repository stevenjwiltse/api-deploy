CREATE barbershop;
USE barbershop;

-- User Table
CREATE TABLE user (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    firstName VARCHAR(50) NOT NULL,
    lastName VARCHAR(50) NOT NULL,
    email VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(50) NOT NULL,
    phoneNumber VARCHAR(10) UNIQUE NOT NULL,
    is_admin BOOLEAN DEFAULT FALSE
);

-- Barber Table
CREATE TABLE barber (
    barber_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT UNIQUE NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE
);

-- Appointment Table
CREATE TABLE appointment (
    appointment_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    barber_id INT NOT NULL,
    status ENUM('pending', 'confirmed', 'completed', 'canceled') NOT NULL,
    FOREIGN KEY (user_id) REFERENCES user(user_id) ON DELETE CASCADE,
    FOREIGN KEY (barber_id) REFERENCES barber(barber_id) ON DELETE CASCADE
);

-- Service Table
CREATE TABLE service (
    service_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    duration TIME NOT NULL,
    price DOUBLE(5,2) NOT NULL
);

-- Appointment_Service Table (Many-to-Many Relationship)
CREATE TABLE appointment_service (
    service_id INT,
    appointment_id INT,
    PRIMARY KEY (service_id, appointment_id),
    FOREIGN KEY (service_id) REFERENCES service(service_id) ON DELETE CASCADE,
    FOREIGN KEY (appointment_id) REFERENCES appointment(appointment_id) ON DELETE CASCADE
);

-- Schedule Table
CREATE TABLE schedule (
    schedule_id INT PRIMARY KEY AUTO_INCREMENT,
    barber_id INT NOT NULL,
    appointment_id INT,
    date VARCHAR(10) NOT NULL,
    startTime TIME NOT NULL,
    endTime TIME NOT NULL,
    FOREIGN KEY (barber_id) REFERENCES barber(barber_id) ON DELETE CASCADE,
    FOREIGN KEY (appointment_id) REFERENCES appointment(appointment_id) ON DELETE SET NULL
);

-- Thread Table (Messaging)
CREATE TABLE thread (
    thread_id INT PRIMARY KEY AUTO_INCREMENT,
    recievingUser INT NOT NULL,
    sendingUser INT NOT NULL,
    FOREIGN KEY (recievingUser) REFERENCES user(user_id) ON DELETE CASCADE,
    FOREIGN KEY (sendingUser) REFERENCES user(user_id) ON DELETE CASCADE
);

-- Message Table
CREATE TABLE message (
    message_id INT PRIMARY KEY AUTO_INCREMENT,
    thread_id INT NOT NULL,
    hasActiveMessage BOOLEAN,
    text TEXT NOT NULL,
    timeStamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (thread_id) REFERENCES thread(thread_id) ON DELETE CASCADE
);