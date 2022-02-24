"""
@author: Qinjuan Yang
@time: 2021-12-26 09:59
@desc: 
"""

"""
Import data from file to mysql database.

# table movie
CREATE TABLE IF NOT EXISTS `movie`(
   `movie_id` INT UNSIGNED NOT NULL,
   `title` VARCHAR(100) NOT NULL,
   `publish_year` YEAR,
   `country` VARCHAR(40),
   `rate` FLOAT,
   PRIMARY KEY ( `movie_id` )
)ENGINE=InnoDB DEFAULT CHARSET=utf8;

# table celebrity
CREATE TABLE IF NOT EXISTS `celebrity`(
    `celebrity_id` INT UNSIGNED NOT NULL,
    `chinese_name` VARCHAR(50) NOT NULL,
    `gender` CHAR(1),
    `birth_date` DATE,
    `birth_place` VARCHAR(100),
    PRIMARY KEY (`celebrity_id`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;

# table genre
CREATE TABLE IF NOT EXISTS `genre`(
    `genre_id` INT UNSIGNED NOT NULL,
    `genre_name` VARCHAR(10) NOT NULL,
    PRIMARY KEY (`genre_id`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;


# table country
CREATE TABLE IF NOT EXISTS `country`(
    `country_id` INT UNSIGNED NOT NULL,
    `country_name` VARCHAR(10) NOT NULL,
    PRIMARY KEY (`country_id`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;


# table movie_to_genre
CREATE TABLE IF NOT EXISTS `movie_to_genre` (
    `movie_id` INT UNSIGNED NOT NULL,
    `genre_id` INT UNSIGNED NOT NULL,
    FOREIGN KEY(`movie_id`) REFERENCES movie(`movie_id`),
    FOREIGN KEY(`genre_id`) REFERENCES genre(`genre_id`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;


# table movie_to_country
CREATE TABLE IF NOT EXISTS `movie_to_country` (
    `movie_id` INT UNSIGNED NOT NULL,
    `country_id` INT UNSIGNED NOT NULL,
    FOREIGN KEY(`movie_id`) REFERENCES movie(`movie_id`),
    FOREIGN KEY(`country_id`) REFERENCES country(`country_id`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;

# table movie_to_director
CREATE TABLE IF NOT EXISTS `movie_to_director` (
    `movie_id` INT UNSIGNED NOT NULL,
    `celebrity_id` INT UNSIGNED NOT NULL,
    FOREIGN KEY(`movie_id`) REFERENCES movie(`movie_id`),
    FOREIGN KEY(`celebrity_id`) REFERENCES celebrity(`celebrity_id`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;

# table movie_to_actor
CREATE TABLE IF NOT EXISTS `movie_to_actor` (
    `movie_id` INT UNSIGNED NOT NULL,
    `celebrity_id` INT UNSIGNED NOT NULL,
    FOREIGN KEY(`movie_id`) REFERENCES movie(`movie_id`),
    FOREIGN KEY(`celebrity_id`) REFERENCES celebrity(`celebrity_id`)
)ENGINE=InnoDB DEFAULT CHARSET=utf8;


# Generate mapping file:
./generate-mapping -u root -p root1234 -o /Users/yangqj/Documents/Workspace/KBQA-for-movie/data/kg/kg_movie_mapping.ttl jdbc:mysql:///kg_movie?characterEncoding=utf8

Use mysql-connector-java-5.1.48.jar

"""
import os
import re
import json

import pymysql

data_dir = "../data/douban"


date_pattern = re.compile(r"(?P<year>[\d]{2,4})年((?P<month>0[1-9]|1[0-2])月)?((?P<day>0[1-9]|1\d|2\d|3[0-1])日)?")

genre2id = dict()
genre_id = 0
country2id = dict()
country_id = 0


sql_celebrity = "INSERT INTO `celebrity` (`celebrity_id`, `chinese_name`, `gender`, " \
                "`birth_date`, `birth_place`) VALUES (%s, %s, %s, %s, %s)"
sql_movie = "INSERT INTO `movie` (`movie_id`, `title`, `publish_year`, `rate`) " \
                          "VALUES (%s, %s, %s, %s)"
sql_genre = "INSERT INTO `genre` (`genre_id`, `genre_name`) VALUES (%s, %s)"
sql_country = "INSERT INTO `country` (`country_id`, `country_name`) VALUES (%s, %s)"
sql_movie_to_genre = "INSERT INTO `movie_to_genre` (`movie_id`, `genre_id`) VALUES (%s, %s)"
sql_movie_to_country = "INSERT INTO `movie_to_country` (`movie_id`, `country_id`) VALUES (%s, %s)"
sql_movie_to_director = "INSERT INTO `movie_to_director` (`movie_id`, `celebrity_id`) VALUES (%s, %s)"
sql_movie_to_actor = "INSERT INTO `movie_to_actor` (`movie_id`, `celebrity_id`) VALUES (%s, %s)"


if __name__ == '__main__':
    conn = pymysql.connect(host='127.0.0.1', user='root',
                           password='root1234', db="kg_movie")

    with conn:
        with conn.cursor() as cursor:

            # write celebrity information
            with open(os.path.join(data_dir, "celebrity.json")) as file_celebrity:
                for x, line in enumerate(file_celebrity):
                    celebrity = json.loads(line)
                    if not celebrity: continue

                    birth_date = None
                    if "birth_date" in celebrity:
                        res = date_pattern.match(celebrity["birth_date"])
                        if res:
                            year, month, day = res.group("year"), res.group("month"), res.group("day")
                            # TODO: handle year with two digits
                            if year:
                                month = month if month else "01"
                                day = day if day else "01"
                                birth_date = f"{year}-{month}-{day}"
                    cursor.execute(sql_celebrity, (celebrity["id"], celebrity["name"], celebrity.get("gender"),
                                   birth_date,  celebrity.get("birth_place")))

            # write movie information
            with open(os.path.join(data_dir, "movie.json")) as file_movie:
                for line in file_movie:
                    movie = json.loads(line)
                    if not movie: continue

                    movie_id = int(movie["id"])

                    # write movie information
                    cursor.execute(sql_movie, (movie_id, movie["title"], movie["year"], float(movie["rate"])))

                    # write publish country of movie
                    if "country" in movie:
                        countries = [c.strip() for c in movie["country"].split("/")]

                        for c in countries:
                            if c not in country2id:
                                cursor.execute(sql_country, (country_id, c))
                                country2id[c] = country_id
                                country_id += 1

                        for c in countries:
                            cursor.execute(sql_movie_to_country, (movie_id, country2id[c]))

                    # write genres of movie
                    if "genre" in movie:
                        for g in movie["genre"]:
                            if g not in genre2id:
                                cursor.execute(sql_genre, (genre_id, g))
                                genre2id[g] = genre_id
                                genre_id += 1

                        for g in movie["genre"]:
                            cursor.execute(sql_movie_to_genre, (movie_id, genre2id[g]))

                    # write directors of movie
                    if "directors" in movie:
                        for d in movie["directors"]:
                            cursor.execute(sql_movie_to_director, (movie_id, int(d)))

                    # write actors of movie
                    if "actors" in movie:
                        for a in movie["actors"]:
                            cursor.execute(sql_movie_to_actor, (movie_id, int(a)))

        conn.commit()
