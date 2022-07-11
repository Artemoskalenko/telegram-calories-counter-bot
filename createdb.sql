create table info(
    purpose varchar(255),
    user_weight integer,
    calories_limit integer,
    proteins_limit integer,
    fats_limit integer,
    carbohydrates_limit integer
);

create table dish(
    codename varchar(255) primary key,
    name varchar(255),
    calories real,
    proteins real,
    fats real,
    carbohydrates real,
    aliases text
);

create table meal(
    id integer primary key,
    weight integer,
    dish_codename varchar(255),
    calories real,
    proteins real,
    fats real,
    carbohydrates real,
    created datetime,
    FOREIGN KEY(dish_codename) REFERENCES dish(codename)
);

insert into dish (codename, name, calories, proteins, fats, carbohydrates, aliases)
values
    ("chicken fillet", "филе", 145.4, 23.4, 5, 1.3, "филе куриное, курица, котлета, котлета куриная, куриная котлета"),
    ("rice", "рис", 344, 6, 0, 78, ""),
    ("buckwheat", "гречка", 266.3, 9.3, 2.5, 51.6, ""),
    ("fried eggs", "яйца жареные", 240, 15.9, 19.3, 1, ""),
    ("eggs", "яйца", 157, 12.7, 11.5, 0.7, ""),
    ("cottage cheese", "творог", 155.3, 16.7, 9, 2, ""),
    ("milk", "молоко", 68, 3, 4, 5, ""),
    ("bananas", "бананы", 96, 1.5, 0.5, 21, "банан");

insert into info(purpose, user_weight, calories_limit, proteins_limit, fats_limit, carbohydrates_limit)
values
    ("Набор", 80, 2640, 160, 80, 320);
