drop database if exists college_parking_lot;
create database college_parking_lot;
use college_parking_lot;

CREATE TABLE User_table (
    UserID CHAR(13) PRIMARY KEY ,
    UserName VARCHAR(50) NOT NULL,
    PhoneNumber VARCHAR(10) NOT NULL,
    UserType ENUM('Student','Employee','Visitor')
);


CREATE TABLE Vehicle (
    VehicleID INT PRIMARY KEY,
    UserID CHAR(13),
    VehicleType ENUM('TwoWheeler', 'FourWheeler') NOT NULL
);

CREATE TABLE ParkingRecord (
    RecordID INT AUTO_INCREMENT PRIMARY KEY,
    UserID CHAR(13),
    LotName ENUM('GJB', 'FBlock', 'OpenAir') NOT NULL, 
    VehicleID INT NOT NULL,
    EntryTime TIMESTAMP NOT NULL,
    ExitTime TIMESTAMP DEFAULT NULL
);

CREATE TABLE ParkingLot (
    LotName ENUM('GJB', 'FBlock', 'OpenAir') NOT NULL PRIMARY KEY,
    Capacity INT NOT NULL,
    Count INT DEFAULT 0,
    Availability BIT(1) DEFAULT 1
);

CREATE TABLE TransactionLog (
    TransactionID INT AUTO_INCREMENT PRIMARY KEY,
    UserID CHAR(13),
	PassID INT,
    Amount DECIMAL(10, 2) NOT NULL,
    TransactionDate DATE NOT NULL,
    PaymentMethod ENUM('UPI', 'Cash') NOT NULL
);

CREATE TABLE ParkingPass (
    PassID INT AUTO_INCREMENT PRIMARY KEY,
    UserID CHAR(13),
    LotName ENUM('GJB', 'FBlock', 'OpenAir') NOT NULL,
    PassType ENUM('Monthly', 'Yearly') NOT NULL,
    IssueDate DATE NOT NULL,
    ExpiryDate DATE NOT NULL
);

alter table Vehicle add FOREIGN KEY (UserID) REFERENCES User_table(UserID) ON DELETE CASCADE;

alter table ParkingRecord add FOREIGN KEY (UserID) REFERENCES User_table(UserID) ON DELETE CASCADE;
alter table ParkingRecord add FOREIGN KEY (VehicleID) REFERENCES Vehicle(VehicleID) ON DELETE CASCADE;
alter table ParkingRecord add FOREIGN KEY (LotName) REFERENCES ParkingLot(LotName) ON DELETE CASCADE;

alter table TransactionLog add FOREIGN KEY (UserID) REFERENCES User_table(UserID) ON DELETE CASCADE;
alter table TransactionLog add FOREIGN KEY (PassID) REFERENCES ParkingPass(PassID) ON DELETE CASCADE;
 
alter table ParkingPass add FOREIGN KEY (UserID) REFERENCES User_table(UserID) ON DELETE CASCADE;
alter table ParkingPass add FOREIGN KEY (LotName) REFERENCES ParkingLot(LotName) ON DELETE CASCADE;


-- Insert dummy data into User_table
INSERT INTO User_table (UserID, UserName, PhoneNumber, UserType)
VALUES
('PES1UG21CS001', 'John Doe', '1234567890', 'Student'),
('PESEMPCS21001', 'Jane Smith', '9876543210', 'Employee'),
('PES21VISID001', 'Bob Johnson', '4567890123', 'Visitor');

-- Insert dummy data into Vehicle
INSERT INTO Vehicle (VehicleID, UserID, VehicleType)
VALUES
(1,'PES1UG21CS001', 'TwoWheeler'),
(3,'PESEMPCS21001', 'FourWheeler'),
(2,'PES21VISID001','FourWheeler');


-- Insert dummy data into ParkingLot
INSERT INTO ParkingLot (LotName, Capacity, Count, Availability)
VALUES
('GJB', 100, 0, 1),
('FBlock', 100, 0, 1),
('OpenAir', 100, 0, 1);

-- Insert dummy data into ParkingPass
INSERT INTO ParkingPass (PassID, UserID, PassType, LotName, IssueDate, ExpiryDate)
VALUES
(1, 'PES1UG21CS001', 'Monthly', 'GJB', '2023-01-01', '2023-02-01'),
(2, 'PESEMPCS21001', 'Monthly','FBlock', '2023-01-01', '2023-02-01');


-- Insert dummy data into ParkingRecord
INSERT INTO ParkingRecord (RecordID, UserID, LotName, VehicleID, EntryTime, ExitTime)
VALUES
(1, 'PES1UG21CS001', 'GJB', 1, '2023-01-01 08:00:00', '2023-01-01 18:00:00'),
(2, 'PESEMPCS21001', 'FBlock', 2, '2023-01-02 09:30:00', '2023-01-02 17:00:00'),
(3, 'PES21VISID001', 'OpenAir', 1, '2023-01-03 12:00:00', NULL);

-- Insert dummy data into TransactionLog
INSERT INTO TransactionLog (TransactionID, UserID, PassID, Amount, TransactionDate, PaymentMethod)
VALUES
(1, 'PES1UG21CS001', 1, 100.00, '2023-01-01', 'UPI'),
(2, 'PESEMPCS21001', 2, 100.00, '2023-01-02', 'Cash'),




DELIMITER //

CREATE PROCEDURE CheckIn(
    IN p_UserID CHAR(13),
    IN p_LotName ENUM('GJB', 'FBlock', 'OpenAir')
)
BEGIN
    DECLARE v_VehicleID INT;

    -- Get VehicleID from the User table
    SELECT VehicleID INTO v_VehicleID
    FROM Vehicle
    WHERE UserID = p_UserID;

    -- Check if the user exists and has a vehicle
    IF v_VehicleID IS NOT NULL THEN
        -- Perform the check-in operation
        INSERT INTO ParkingRecord (UserID, LotName, VehicleID, EntryTime, ExitTime)
        VALUES (p_UserID, p_LotName, v_VehicleID, NOW(), NULL);

        -- Update ParkingLot Count and Availability
        UPDATE ParkingLot
        SET Count = Count + 1,
            Availability = (Capacity > (Count + 1))
        WHERE LotName = p_LotName;

        SELECT 'Check-in successful.' AS Result;
    ELSE
        SELECT 'User does not exist or has no vehicle.' AS Result;
    END IF;
END //

DELIMITER ;


DELIMITER //
CREATE TRIGGER DecrementCountTrigger
AFTER UPDATE ON ParkingRecord
FOR EACH ROW
BEGIN
    IF NEW.ExitTime IS NOT NULL AND OLD.ExitTime IS NULL THEN
        UPDATE ParkingLot 
        SET Count = Count - 1,
			Availability = (Capacity > (Count - 1))
		WHERE LotName = NEW.LotName;       
    END IF;
END //
DELIMITER ;


desc User_table;
desc Vehicle;
desc ParkingRecord;
desc ParkingLot;
desc TransactionLog;
desc ParkingPass;
