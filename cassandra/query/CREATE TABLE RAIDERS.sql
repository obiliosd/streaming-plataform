USE sparkstreaming;

CREATE TABLE raiders (
identifier int,
country text,
region text,
coordinatesTime timestamp,
coordinates list<double>,
prediction int,
PRIMARY KEY ((country,region),identifier));

INSERT INTO raiders (identifier, country,region, coordinatesTime ,coordinates,prediction) 
VALUES (1, 'Spain', 'Barcelona', '2021-10-17T13:18:20.766Z', [2.1535177931411975,41.39341576682141], 5);

select * from raiders;

drop table raiders;
