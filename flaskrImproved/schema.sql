drop table if exists entries;
create table entries (
  id integer primary key autoincrement,
  title text not null,
  text text not null
);
drop table if exists users;
create table users (
  user text primary key,
  pass text not null
);