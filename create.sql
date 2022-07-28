use devx;

CREATE TABLE cost (
    id INT NOT NULL AUTO_INCREMENT,
    cost DOUBLE NOT NULL,
    created_at DATETIME NOT NULL,
    unit VARCHAR(10) NOT NULL,
    app VARCHAR(50),
    PRIMARY KEY(id)
) CHARSET=utf8;

CREATE TABLE price (
    id INT NOT NULL AUTO_INCREMENT,
    price DOUBLE NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
    unit VARCHAR(10) NOT NULL,
    aws_service VARCHAR(200),
    PRIMARY KEY(id)
) CHARSET=utf8;

CREATE TABLE capacity (
    id INT NOT NULL AUTO_INCREMENT,
    capacity INT NOT NULL,
    created_at DATETIME NOT NULL,
    app VARCHAR(50),
    PRIMARY KEY(id) 
) CHARSET=utf8;

CREATE TABLE resource_usage (
    id INT NOT NULL AUTO_INCREMENT,
    resource_usage INT NOT NULL,
    metric_id INT NOT NULL REFERENCES metric(id),
    created_at DATETIME NOT NULL,
    unit VARCHAR(10) NOT NULL,
    app VARCHAR(50),
    PRIMARY KEY(id)
) CHARSET=utf8;

CREATE TABLE days_of_usage (
    id INT NOT NULL AUTO_INCREMENT,
    metric_id INT NOT NULL REFERENCES metric(id),
    days_usage INT NOT NULL,
    day DATETIME NOT NULL,
    unit VARCHAR(10) NOT NULL,
    PRIMARY KEY(id)
) CHARSET=utf8;

CREATE TABLE months_of_usage (
    id INT NOT NULL AUTO_INCREMENT,
    metric_id INT NOT NULL REFERENCES metric(id),
    months_usage INT NOT NULL,
    month DATETIME NOT NULL,
    unit VARCHAR(10) NOT NULL,
    PRIMARY KEY(id)
) CHARSET=utf8;

CREATE TABLE metric (
    id INT NOT NULL AUTO_INCREMENT,
    metric VARCHAR(50) NOT NULL,
    PRIMARY KEY(id)
) CHARSET=utf8;