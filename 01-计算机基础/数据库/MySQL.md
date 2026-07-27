# 一、MYSQL 基础

- char、varchar 的区别

- char 0-255 字符，自动填充空格。varchar 0-65535 字符。

## (一) DQL（数据查询语言）

```SQL
SELECT [DISTINCT] c1 [AS a1],..			# 4
FROM table1,table2						# 1
WHERE conditions						# 2
[GROUP BY c1,c2 [HAVING count(*) > 1]]	# 3
[ORDER BY c1 ASC|DESC, c2 ASC|DESC]		# 5
[LIMIT srcIndex, rows] ;				# 6
```

### 1. 条件查询

|   |   |
|---|---|
|比较运算符|说明|
|BETWEEN ... AND ...|在指定范围内(含最小、最大值)。|
|IN (...)|在指定列表中，多选一。|
|LIKE|_ 匹配单个字符, **%** 匹配任意个字符。|
|IS NULL||

### 2. 聚合函数

- count、max、min、avg、sum

### 3. 分组查询

- where 在分组前过滤，having 对分组结果过滤。
- where 不能对聚合函数判断，having 可以对聚合函数判断。
- 执行顺序：where -> 聚合函数 -> having。

```SQL
SELECT address, COUNT(*) AS cnt FROM emp WHERE age < 45 GROUP BY address HAVING cnt >= 3;
```

### 4. 分页查询

- limit 第一个参数表示起始索引，第二个参数表示行数。如果省略第一个参数，则表示从索引0开始。

```SQL
SELECT id FROM emp LIMIT 10, 10;
```

### 5. 连接查询

- 内连接

```SQL
SELECT * FROM emp e, department d WHERE e.id = d.id;
SELECT * FROM emp e [INNER] JOIN department d ON e.id = d.id;
```

- 外连接

```SQL
SELECT * FROM emp e LEFT [OUTER] JOIN department d ON e.id = d.id; 
SELECT * FROM emp e RIGHT [OUTER] JOIN department d ON e.id = d.id;
```

### 6. 联合查询

- 将多次查询的结果按行拼接起来形成一个更长的结果表。
- union all 会直接将结果拼到一起，union 会对合并后结果进行去重。

```SQL
SELECT aid FROM 表A ...
UNION [ALL]
SELECT bid FROM 表B ....;
```

### 7. 子查询

- 列子查询：**IN、NOT IN、ANY、SOME、ALL**。
- 行子查询：**=、!=、IN、NOT IN**。
- 表子查询：**IN**。

## (二) 函数

### 1. 字符串函数

```SQL
CONCAT(s1,...,sn) 			# 字符串拼接，将s1 ~ sn拼接成一个字符串.
LOWER(str) 					# 将字符串str全部转为小写.
UPPER(str) 					# 将字符串str全部转为大写.
LPAD(str,n,pad)				# 用字符串pad对str的左边进行填充，直到n个字符长度.
RPAD(str,n,pad)				# 用字符串pad对str的右边进行填充，直到n个字符长度.
TRIM(str) 					# 去掉字符串头部和尾部的空格.
SUBSTRING(str,start,len)	# 返回从字符串str从start位置起的len个长度的字符串.
```

### 2. 数值函数

```SQL
CEIL(x) 		# 向上取整.
FLOOR(x) 		# 向下取整.
MOD(x,y) 		# 返回x % y.
RAND() 			# 返回0~1内的随机数.
ROUND(x,y) 		# 求参数x的四舍五入的值，保留y位小数.
```

### 3. 日期函数

```SQL
CURDATE()			# 返回当前日期.
CURTIME()			# 返回当前时间.
NOW()				# 返回当前日期和时间.
YEAR(date)			# 获取指定date的年份.
MONTH(date)			# 获取指定date的月份.
DAY(date) 			# 获取指定date的日期.
DATE_ADD(date, INTERVAL expr type)# 返回一个日期/时间值加上一个时间间隔expr后的时间值
DATEDIFF(date1,date2)	# 返回起始时间 date1 和 结束时间date2之间的天数.
```

### 4. 流程函数

```SQL
IF(val, t, f) 			# 如果val为true，则返回t，否则返回f
IFNULL(val1 , val2)		# 如果val1为空，返回val2，否则返回val1
```

```SQL
CASE			# 依次判断 when 之后的表达式是否为真，如果为真，则返回对应结果
    WHEN [expr1] THEN [res1]
    ...
    ELSE [default] END

CASE [expr]		# 依次判断expr值是否等于when之后的value，如果等于则返回对应结果
    WHEN [val1] THEN [res1] 
    ... 
    ELSE [default] END
```

## (三) 约束

- 约束作用于字段，用来对存入表中的数据进行限制。

	|约束|说明|
	|---|---|
	|非空约束 **not null**|限制该字段数据不能为 null|
	|唯一约束 **unique**|限制该字段数据唯一、不重复|
	|主键约束 **primary key**|设置某些字段作为主键，非空且唯一|
	|默认约束 **default**|保存数据时，如果未指定该字段的值，则采用默认值|
	|检查约束 **check()**|检查该字段数据是否满足某条件|
	|外键约束 **foreign key**|让两张表的数据之间建立连接，一张表的数据对应另一张表的主键|

### 1. 列约束

- ①**not null**，②**default**，③**primary key**，④**unique**，⑤**check**

```SQL
# 建表时添加约束
create table stu(
    id 		int primary key,
    name 	char(30) not null,
    ...
);
# 单独修改列约束
alter table stu modify column id int not null / default 18 / primary key / unique / check(id >= 0);
```

### 2. 表约束

- ①**primary key**，②**unique**，③**check**，④**foreign key**

```SQL
1. 建表时添加
create table emp(
    id       int,
    ...
    [constraint] primary key (id),
    [constraint idx1] unique (idcard),
    [constraint chk1] check (age >= 0 and age <= 200),
    [constraint fk1] foreign key (deId) references depart (id) [on update cascade] [on delete set null]
);

2. 单独添加
alter table emp add primary key (id) /
					unique (idcard) /
					check (age >= 0 and age <= 200) /
					foreign key (departId) references department (id);

3. 删除约束
alter table emp drop primary key / index idx1 / check chk1 / foreign key fk1;			
```

### 3. 外键删除/更新

```SQL
foreign key (uid) references uuser(id) on update cascade on delete set null
```

|   |   |
|---|---|
|行为|说明|
|**no action / restrict**|默认行为，当删除/更新某记录时，检查该记录是否有外键正在使用，如果有，则不允许删除/更新。|
|**cascade**|当删除/更新某记录时，检查该记录是否有外键正在使用，如果有，则级联地删除/更新其它表对应的记录。|
|**set null**|当删除/更新某记录时，检查该记录是否有外键正在使用，如果有，则设置其他表对应的记录为 null。|
|**set default**|当删除/更新某记录时，检查该记录是否有外键正在使用，如果有，则设置其他表对应的记录为默认值。其中，Innodb 引擎不支持该设置。|

## (四) 触发器

- 在 **insert/update/delete** 之前(**before**)或之后(**after**)，触发并执行触发器中定义的SQL语句集合。

```SQL
CREATE TRIGGER trigger_name
BEFORE|AFTER  INSERT|UPDATE|DELETE
ON tbl_name FOR EACH ROW 	-- 行级触发器
BEGIN
    -- SQL
END;
```

```SQL
SHOW TRIGGERS ;
```

```SQL
-- 如果没有指定 schema_name，默认为当前数据库。
DROP TRIGGER [schema_name.]trigger_name ; 
```

# 二、MySQL 执行 SQL 的过程

![](https://cdn.nlark.com/yuque/0/2026/png/46298582/1773333366171-b92ad647-538c-44b9-8bb7-3747769820f2.png)

## (一) 查询语句执行过程

1. 连接器与客户端通过 TCP 三次握手建立连接，校验客户端用户名与密码，获取该用户的权限配置，且本次连接所有操作都仅参考此次权限配置。
2. 如果 SQL 是 select 语句，则检查查询缓存是否有结果。如果表有更新操作，该表的查询缓存就被清空。MySQL8.0 开始，已经删除 Server 层的查询缓存。
3. 解析器对 SQL 进行词法分析、语法分析。
4. 预处理器会检查表或字段等是否存在。优化器会进行优化并生成执行计划。最后执行器/执行引擎执行语句，通过 API 与存储引擎交互。

- **主键索引查询**：第一次查询调用 read_first_record 指向的函数，因为 type 为 const，调用索引扫描的接口，并把条件给存储引擎进行查询。如果没有记录则返回 Error，否则返回第一条记录。执行器判断该记录是否符合条件，符合发送给客户端；否则调用 read_record 指向的函数，但是 type 为 const 所以指向一个返回-1 的函数，执行器推出循环即结束查询。
- **全表扫描**：第一次查询调用 read_first_record 指向的函数，因为 type 为 all，调用全表扫描的接口，并把条件给存储引擎进行查询。如果没有记录则返回 Error，否则返回第一条记录，执行器判断该记录是否符合条件，符合发送给客户端。执行器循环内接着调用 read_record 指向的函数，要求存储引擎继续读刚才记录的下一条记录，执行器则判断是否符合条件，符合则发送给客户端，直到遍历全表。
- **索引下推**：索引下推能够减少二级索引在查询时的回表操作，提高查询的效率。

- Server 层调用 API 定位到满足查询条件的第一条二级索引记录；
- 存储引擎定位到二级索引后，先不执行回表操作，而是先判断一下该索引中包含的列的条件是否成立。如果条件不成立，则直接跳过该二级索引。如果成立，则执行回表操作，将完成记录返回给 Server 层。
- Server 层再判断其他的查询条件是否成立，如果成立则将其发送给客户端；否则跳过该记录，然后向存储引擎索要下一条记录。

## (二) update 语句执行过程

1. 执行器调用 InnoDB 的 API，查找主键索引记录：如果该记录在 buffer pool 中，则直接读取并返回给执行器；如果不在，则先从磁盘中读取到 buffer pool，再返回给执行器。
2. 执行器会对比记录更新前后是否一样：如果一样则停止更新流程；如果不一样，则将更新前后的记录都当作参数传给 InnoDB。
3. InnoDB 首先将记录更新前的状态记录到位于 Buffer pool 中的 Undo 页中，然后将该 Undo 页的修改记录到 Redo log buffer 中。
4. InnoDB 首先修改 Buffer pool 中的数据页，并标记为脏页，然后将修改写到 Redo log buffer 中。脏页不会立即被写入磁盘，由后台线程选择一个合适的时机将脏页写入到磁盘，即 WAL 技术。
5. 该更新语句执行完之后，Server 层生成 binlog 日志并写入 binlog cache，在事务提交后，会统一将该线程的 binlog cache 全部刷新到 page cache，后续由 sync_binlog 控制刷盘的频率和时机。
6. 事务提交后，开始两阶段提交。

![](https://cdn.nlark.com/yuque/0/2025/png/46298582/1765432349069-951fe17a-4a81-4491-bad8-e9b26cc8108a.png)

# 三、事务

- 事务是一组不可分割的操作的集合，这组操作要么全部执行成功，要么全部执行失败。
- mysql 默认每一条 SQL 语句作为一个独立事务，自动开启、提交、回滚事务。

## (一) 事务四大特性 ACID

- **原子性 Atomicity**：事务是不可分割的最小操作单元，要么全部成功，要么全部失败。

- 原子性通过 Undo log 保证的。

- **一致性 Consistency**：事务开始前和结束后，数据库的完整性没有受到破坏。

- 一致性是由原子性、隔离性、持久性保证。

- **隔离性 Isolation**：并发事务之间不会由于交叉执行导致数据不一致。

- 隔离性通过 MVCC (隐藏字段、Undo log 版本链、快照) + 锁保证。

- **持久性 Durability**：事务一旦提交或回滚，它对数据库中的数据的改变就是永久的。

- 持久性由 Redo log、bin log 保证。

## (二) 并发事务的 3 种问题

### 1. 脏读

- 一个事务读到了另一个事务还没有提交的数据。若对方回滚，则数据无效。

### 2. 不可重复读

- 同一个事务内先后读取同一条记录，但两次读取的数据不一致。
- **可重复读**指同一事务中多次读取数据，能够保证所读数据都是一样的。

### 3. 幻读

- 一个事务查询数据时，没有对应记录；但是插入数据时，又发现数据已存在。
- **快照读**：不加锁的 select 就是快照读，读取的是数据的可见版本，有可能是历史数据，非阻塞读。通过 **MVCC** 在**读已提交**和**可重复读**级别下，通过不同的 ReadView 生成机制尽可能避免幻读。
- **当前读**：读取数据的最新版本，读取时要保证其它并发事务不能修改当前记录。对当前读取的记录的索引项加**邻键锁**，如果有其他事务在邻键锁范围内插入记录会被**阻塞**。如：select ... lock in share mode/ for update、update、insert、delete。

#### 一、可重复读仍会出现的幻读

1. 一个事务在明知主键记录不存在的情况下，仍然更新数据，且在这两个操作之间恰好有另一个事务插入该主键记录，此时该事务完成更新后就可以查到该记录。

![](https://cdn.nlark.com/yuque/0/2026/png/46298582/1773575171231-fbca059e-eda5-43af-b772-f800f3ac3a34.png)

2. 第一次范围查询使用快照读，第二次范围查询使用当前读，且两次操作之间恰好有一个事务插入了记录。

- T1 时刻：事务 A 先执行「快照读」：select * from t_test where id > 100 得到了 3 条记录。
- T2 时刻：事务 B 插入一个 id= 200 的记录并提交。
- T3 时刻：事务 A 再执行「当前读语句」 select * from t_test where id > 100 for update 就会得到 4 条记录，此时也发生了幻读现象。

## (三) 事务隔离级别

- InnoDB 默认 Repeatable Read 级别，并通过**邻键锁**解决了绝大部分幻读问题。

|   |   |   |   |   |
|---|---|---|---|---|
|隔离级别|脏读|不可重复读|幻读|实现原理|
|**读未提交**<br><br>**Read uncommitted**|√|√|√|直接读取最新数据|
|**读已提交**<br><br>**Read committed**|×|√|√|事务中每一次执行快照读时生成新的 ReadView|
|**可重复读**<br><br>**Repeatable Read (默认)**|×|×|√|仅在事务中第一次执行快照读时生成 ReadView，后续复用该 ReadView。|
|**串行化**<br><br>**Serializable**|×|×|×|强制所有事务顺序执行。将所有查询转换为当前读，加读写锁。|

```SQL
SELECT @@TRANSACTION_ISOLATION;
SET [SESSION | GLOBAL] TRANSACTION ISOLATION LEVEL {READ UNCOMMITTED | READ COMMITTED | REPEATABLE READ | SERIALIZABLE };
```

## (四) savepoint 保存点

```SQL
SAVEPOINT sp; 				# 设置保存点。
ROLLBACK TO SAVEPOINT sp;	# 回滚到指定的保存点。
RELEASE SAVEPOINT sp;		# 释放指定保存点。
```


# 四、锁

## (一) 全局锁（必须手动加锁）

- 对整个数据库加锁，加锁后数据库就处于**只读**状态，DML、DDL 以及 DQL 的事务提交语句都会被阻塞；其中如果 DQL 查询的表在全局锁之前已经加载到内存，可以读取已加载数据。

```SQL
# 加全局锁
flush tables with read lock;
# 释放锁
unlock tables ;
```

- 全局锁一般用来进行数据库备份。

- 如果在主库上备份，那么在备份期间都不能执行更新。
- 如果在从库上备份，那么在备份期间从库不能执行主库同步过来的 binlog，会导致主从延迟。
- 加上参数 --single-transaction 参数，在备份前开启事务，创建 ReadView 这样备份的数据就是开启事务时的数据。只适用于支持可重复读的存储引擎。

```SQL
mysqldump -uroot –p1234 itcast > itcast.sql
mysqldump --single-transaction -uroot –p123456 itcast > itcast.sql
```

## (二) 表级锁

### 1. 表锁（必须手动加锁）

- **表写锁**是互斥锁，会阻塞其它线程的读写该表，阻塞当前线程读写其他表。
- **表读锁**是共享锁，会阻塞其它线程、当前线程的写该表，阻塞当前线程读写其他表。

```SQL
lock tables 表名 read/ write;
unlock tables;
```

### 2. 元数据锁（meta data lock，MDL）

- MDL 锁由系统自动控制，访问任意表**自动加锁**，事务结束自动释放。
- 主要作用是维护表中元数据与数据的一致性，在表上有活动事务的时候，不可以对元数据进行写入操作，从而避免 DML 与 DDL 之间的冲突。
- 当对一张表进行增删改查时，加 MDL 共享锁；当对表结构进行改变时（alter），加 MDL 排他锁。
- 如果有事务获取 MDL 排他锁失败，导致该线程阻塞在 MDL 排他锁上，后续所有申请 MDL 共享锁的线程都会阻塞。因为所有申请 MDL 锁的操作会组成一个队列，获取写锁优先级高于读锁。

### 3. 意向锁

- 为了避免行锁与表锁的冲突，引入了意向锁。用来快速判断表中是否有记录被行锁。
- 当事务中加共享锁/排他锁时，会自动对该表加意向共享锁/排他锁。当事务结束后，意向锁就会自动释放。
- **意向共享锁（IS）**: 与表读锁兼容，与表写锁互斥。
- **意向排他锁（IX）**: 与表锁互斥，意向锁之间不会互斥。

|   |   |   |
|---|---|---|
|SQL语句|锁类型|说明|
|lock tables t1 read|**表读锁**<br><br>SHARED_READ_ONLY|与读锁兼容，写锁互斥|
|lock tables t1 write|**表写锁**<br><br>SHARED_NO_READ_WRITE|与所有锁互斥|
|select ... lock in share mode|**MDL 共享锁、意向共享锁**<br><br>SHARED_READ|与表读锁、MDL 共享锁兼容，与表写锁、MDL 互斥锁互斥|
|insert / delete / update / select ... for update|**MDL 共享锁、意向排他锁**<br><br>SHARED_WRITE|与 MDL 共享锁兼容，与 表锁、MDL 互斥锁互斥|
|alter table ...|**MDL 排他锁**<br><br>EXCLUSIVE|与所有锁互斥|

### 4. AUTO_INC 锁/自增锁

- 主键的 AUTO_INCREMENT 属性就是通过 AUTO_INC 锁实现。
- AUTO_INC 锁不是在事务提交后释放，而是**插入语句完成后立即释放**。当一个事务持有一张表的 AUTO_INC 锁时，其他事务向该表执行插入语句都会被阻塞。

## (三) 行级锁

- 行级锁加锁对象是**索引项**，基本单位是邻键锁，但是在不同情况可能会被优化为记录锁、间隙锁。
- 直接使用主键索引时对主键索引加邻键锁，使用二级索引对二级索引项加邻键锁且对存在的主键索引加记录锁。
- 当查询没有使用索引时，意味着**全表扫描**，会按搜索顺序给所有记录加上邻键锁，容易导致阻塞和死锁。
- **唯一索引**上的**等值**查询

- 记录**存在**时，对该索引加**记录锁**。
- 记录**不存在**时，找到第一个大于目标记录的索引后对前面的间隙加**间隙锁**。

- **唯一索引**上的**范围**查询，会访问到不满足条件的第一个值为止。
- **非唯一索引**上的**等值**查询

- 记录存在时，所有符合条件的索引都加邻键锁，第一个不满足条件的索引加**间隙锁**。对这些存在的记录的主键索引加记录锁。
- 记录不存在时，扫描到的第一个不符合条件的索引加**间隙锁**，主键索引不加锁。

### 1. 记录锁/行锁**（Record Lock）**

- 记录锁对某一行对应的索引项加锁，防止其他事务对此行进行 update 和 delete。在**读已提交、可重复读、串行化**隔离级别下都支持。
- **共享锁（S）**：允许一个事务读取一行，与共享锁兼容，与排他锁互斥。
- **排他锁（X）**：只有获取排他锁的事务才能更新数据。

|   |   |
|---|---|
|记录锁|SQL语句|
|**共享锁（S）**|select ... lock in share mode|
|**排他锁（X）**|select ... for update、insert、update、delete|

- 针对**唯一索引**进行检索时，对**已存在的记录**进行**等值查询**时，会自动优化为**行锁**。
- 如果检索时索引失效，行锁就会升级为表锁。

### 2. 间隙锁**（Gap Lock）**

- 间隙锁对索引之间的间隙 **( )** 加锁，确保索引间隙不变，防止其他事务在间隙内插入数据，产生幻读。在**可重复读**隔离级别下支持。
- 间隙锁之间可以兼容，也就是不同事务可以持有包含**公共区间**的间隙锁。

### 3. 临键锁**（Next-Key Lock）**

- 临键锁是行锁和间隙锁的组合，同时锁住索引项和索引前面的间隙 **( ]** 。
- 临键锁只在 **Repeatable Read** 隔离级别下支持。

### 4. 插入意向锁

- 事务在插入记录时，如果插入位置被其他事务加了间隙锁，则该事务会生成一个插入意向锁，并设置为等待状态，然后阻塞直到间隙锁释放。

## (四) SQL 死锁

- `innodb_deadlock_detect = on` 开启死锁检测，定期检测死锁，有死锁存在就会回滚其中部分事务。
- `innodb_lock_wait_timeout` 设置锁等待的超时时间，如果锁超时就回滚事务。

# 五、存储引擎

```SQL
show engines;		-- 查询支持的存储引擎
```

## (一) MyISAM

- MySQL 早期默认存储引擎，访问速度快。
- 不支持事务，不支持外键。
- 支持表锁，不支持行锁。
- sdi 存储表结构，MYD 存储数据，MYI 存储索引。

## (二) Memory

- 表数据存储在内存中，支持 hash索引，sdi 存储表结构。

|   |   |   |   |
|---|---|---|---|
||InnoDB|MyISAM|Memory|
|存储限制|64TB|有|有|
|**事务**安全|支持|-|-|
|**锁**机制|行锁|表锁|表锁|
|支持**外键**|支持|-|-|
|空间使用|高|低|-|
|内存使用|高|低|中等|
|批量插入速度|低|高|高|
|**B+Tree** 索引|支持|支持|支持|
|**Hash** 索引|不支持|不支持|支持|
|**R-tree** 索引|不支持|支持|不支持|
|**Full-text** 索引|支持 (5.6 版本之后)|支持|不支持|

# 六、InnoDB

- DML 操作遵循 ACID 模型，支持**事务**。
- **行级锁**，提高并发性能。
- 支持**外键**约束，能保证数据完整性和正确性。

## (一) 逻辑存储结构

### 1. **表空间**

- 表空间文件就是 .ibd 文件，包含多个段。`innodb_file_per_table` 默认 1，表示每一张表单独一个 .ibd 文件。

### 2. 段 Segment

- 数据段（Leaf node segment）：B+树中叶子节点所在的区的集合。
- 索引段（Non-leaf node segment）：B+树中非叶子节点所在的区的集合。
- 回滚段（Rollback segment）：由存储回滚数据的区的集合。
- 一个段包含多个区。

### 3. 区 Extent

- 每个区大小 1M，默认一个区包含 64 个连续页。InnoDB 申请空间时按区申请，同一个区中的页也是连续的，范围查询时就可以顺序 IO。在数据量大时，为了保证页的连续性，InnoDB 每次从磁盘申请 4-5 个区。

### 4. 页 Page

- InnoDB 引擎存储、读取数据的最小单位，每个页默认 16K，一个页包含多个行。常见页有数据页、undo 日志页、溢出页等。

1. 数据页

- 一个数据页包含文件头、文件尾、页头、页目录、用户记录、虚拟最大最小记录。
- 文件头中保存页信息，包括两个指向前一个和下一个数据页的指针。
- 所有记录按照**主键顺序**组成**单向链表**，并且所有记录+虚拟最大最小记录被划分为**若干个组**。第一个组只包含一个虚拟最小记录，虚拟最小记录下一个记录就是最小用户记录；最后一个组包含若干条用户记录和虚拟最大记录；其他组同样包含若干条记录。每个组的最后一个记录的记录头信息中有一个字段会记录该分组中一共有多少条记录。
- **页目录**中包含若干个**槽 slot**，槽数量=分组数量，槽按顺序保存对应分组中最后一条记录的偏移量。因此按主键查找用户记录时，可以使用二分法进行查找，然后在分组内按链表遍历查找。

2. 索引页

- 索引页中每一条数据只记录主键和页号，其中页号大小固定 4B。

### 5. 行 Row

- InnoDB 引擎中数据是按行存储的，有 Redundant(几乎不用)、Compact、Dynamic和 Compressed 4 种行格式。
- Compact

- 变长字段长度列表记录变长字段的长度，长度<=255 使用 1B 表示，>255 使用 2B 表示。
- NULL 值列表记录允许 NULL 值的列是否为 NULL，1 bit 表示一个列，NULL 值列表不足 1B 填充到 1B。NULL 值不存储实际数据。
- 记录头信息包含：delete_mask 标识数据是否被删除，next_record 指向下一条记录的记录头信息和真实数据之间的位置，record_type 表示当前记录类型等等。
- **row_id** 占 6B，不是必须的。
- **trx_id** 事务 ID，表示该数据由哪个事务生成或修改。占 6B，必须字段。
- **roll_ptr** 指向当前记录上一个版本的指针。占 7B，必须字段。
- 当存在 TEXT、BLOB 等大对象时，可能发生行溢出。COMPACT 会将溢出的数据存储到溢出页，并用 20B 存储溢出页的指针。

![](https://cdn.nlark.com/yuque/0/2026/png/46298582/1773409743990-e1db2fe0-306e-47d1-9ad8-ea77bc4a5a3f.png?x-oss-process=image%2Fcrop%2Cx_0%2Cy_161%2Cw_2336%2Ch_251)

- Dynamic和 Compressed 存储行溢出时，不在数据页存储真实数据，而是将所有数据都存到溢出页，并用 20B 存储溢出页指针。

## (二) MVCC

- 多版本并发控制指维护一个数据的多个版本，使得快照读和写操作之间没有冲突。MVCC 的实现依赖于数据库记录的 3 个隐藏字段、Undo log 日志、ReadView。

### 1. 聚簇索引记录的隐藏列

- 旧版本数据写入 Undo log 中，聚簇索引中最新记录的 roll_ptr 指向 Undo log 中的旧版本，每个版本不断指向前一个旧版本形成版本链。

|   |   |
|---|---|
|隐藏列|含义|
|row_id|如果表没有指定主键，将会生成该隐藏字段作为主键。|
|trx_id|一个事务创建或修改聚簇索引记录时，会将该事务 id 记录在该字段。|
|roll_ptr|回滚指针。事务对聚簇索引记录进行修改时，旧版本记录就会写进 Undo log 中，该列就是指向上一个旧版本记录的指针。|

### 2. ReadView

- 只由快照读生成，ReadView 中只有 4 个字段。每次查询记录时，根据记录的 trx_id 和字段值按如下规则判断是否可见。如果不可见，则顺着版本链向前找到第一个 trx_id<min_trx_id 的旧版本。
- 事务访问记录时，自己更新的记录总是可见的即 trx_id == creator_trx_id。
- 如果记录 trx_id<min_trx_id，该记录是在该快照创建前就被事务提交了，可见。
- 如果记录 trx_id>=max_trx_id，该记录是在该快照创建之后才启动的事务提交的，不可见。
- 如果 min_trx_id <= trx_id < max_trx_id

- 如果 trx_id 在 m_ids 中，说明生成该版本的事务还没提交，不可见。
- 如果 trx_id 不在 m_ids 中，说明生成该版本的事务已经提交，可见。

|   |   |
|---|---|
|字段|含义|
|m_ids|创建该 ReadView 时，数据库中活跃 (启动但没有提交) 的事务 id 集合。|
|min_trx_id|创建该 ReadView 时，活跃事务中最小的事务 id 即 m_ids 的最小值。|
|max_trx_id|预分配给下一个事务的 id，即当前最大事务 id+1。|
|creator_trx_id|创建该 ReadView 的事务的 id。|

### 3. Undo log

- Undo log 是**逻辑日志**，记录事务修改前的数据状态，作用包含两个 : 支持**回滚**（保证事务的**原子性**）和 **MVCC** (多版本并发控制) 。
- Undo log 针对插入、删除、更新会记录不同内容，并有不同的删除机制。

|   |   |
|---|---|
|insert|记录主键，回滚时删除对应主键记录。事务提交后可以立即删除。|
|delete|记录完整的行数据，回滚时重新插入。回滚、快照读都需要，事务提交后不能立即删除，而是将删除标志改为 1，最后由 purge 线程删除。|
|update|记录更新列的旧值，回滚时更新为旧值。回滚、快照读都需要，事务提交不能立即删除。特别的，如果修改主键列，则先 delete，再 insert。|

- 在内存中，Undo log 会被写入 **Buffer Pool** 的 undo 页中。Undo log 刷盘策略和数据页是一致的，并且 undo 页的修改也会被记录到 Redo log 中，实现 Undo log 的持久化。

## (三) Buffer Pool

- 缓存了索引页、数据页、undo页、插入缓存页、自适应哈希索引、锁信息等。
- 读数据时，如果数据在缓冲池中，就会直接读取。写数据时，如果数据在缓冲池中，就会直接修改对应的页，并将页标记为脏页，由后台线程将脏页写回磁盘。
- Buffer pool 默认大小 128MB 连续内存。一部分连续内存划分为大小为 16KB 的**缓存页**，并通过**控制块**管理缓存页，控制块记录页的表空间、页号、缓存页地址、链表节点的指针等。
- Buffer pool 通过 Free 链表管理空闲的页。Free 链表是一个双向链表，链表头记录链表头节点、尾节点、节点数量等，链表节点中保存指向空闲页的控制块的指针。
- Buffer pool 通过 Flush 链表管理脏页。Flush 链表和 Free 链表类似，只是记录的是脏页。
- Buffer pool 通过 LRU 链表管理所有非空闲页 (脏页+干净页)。LRU 链表为了减少预读失效带来的影响，将链表分为前半部分的 young 区、后半部分的 old 区，预读页插入 old 区的头部，真正使用的才加入链表头。

## (四) Redo log

- Redo log 是**物理日志**，会记录数据页、undo 页等发生了什么修改，用来实现持久性。例如：对 A 表空间的 B 数据页的 C 偏移量进行了 X 更新操作。
- 当 Buffer Pool 中的页发生修改的同时会被标记为**脏页**，然后本次修改会被记录到 **Redo log buffer** 中。**后台线程**会在合适时间将脏页刷新回磁盘，即 **WAL** (Write-Ahead Logging) 技术。
- 事务提交时，由`innodb_flush_log_at_trx_commit`参数控制 Redo log 刷盘策略，默认是**直接持久化到磁盘**。也可以设置为不主动触发、或写入 page cache，由后台线程 Master 每隔 1 秒刷盘一次。
- 在内存中，Redo log 保存在 Redo log buffer 中（Log Buffer 的一部分），当遇到事务提交、Checkpoint、正常关闭、Master 后台线程每秒钟会刷盘、Redo Log Buffer 空间占用达到一半时会将 redo log 刷盘。
- 磁盘中同时存在两个 Redo log，采用**循环写**的方式，file0 写满切换到 file1，file1 写满了再切换回 file0。Redo log 刷盘时采用**追加**方式即顺序 IO，速度远比数据页随机 IO 要快。

- InnoDB 用 write_pos 表示 Redo log 当前写到位置，用 checkpoint 表示要擦除的位置。如果 write_pos 追上 checkpoint ，表示 Redo log 满了，MySQL 会被阻塞。

## (五) binlog

- 事务中进行一次增、删、改操作后，**Server** 层会生成一条日志并写入 Server 层的 **binlog cache**，事务提交后，会把该线程的 binlog cache 会统一写入 binlog 文件。此次写入是调用 **write**() 写入到内核的 **page cache**，由 sync_binlog 参数控制 fsync 的频率，默认情况下交由操作系统决定什么时候持久化而不是立即持久化。
- binlog 由 Server 生成，**所有存储引擎**都可以使用，记录的是表结构、表数据在**逻辑层面**的变化。
- binlog 采用**追加写**方式，写满一个文件就会创建一个新的文件继续写，保存全量日志。

|   |   |   |
|---|---|---|
|**格式**|**内容**|**主从复制**|
|**Statement**|**默认**，记录执行的原始 SQL 语句|从库会直接执行 SQL 语句，可能导致主从不一致。|
|**Row**|记录数据行更新后的细节，更新多少行就有多少日志，日志体积比较大。|主从复制一致性强。|
|**Mixed**|混合，自动使用 Statement 或 Row。||

## (六) 两阶段提交

- 事务提交后，Redo log buffer 和 binlog cache 都需要持久化到磁盘，但是这两个是独立的逻辑，可能出现不完全成功，导致数据不一致。
- 两阶段提交分为：准备阶段、提交阶段。

- **准备**阶段：将 XA 事务 ID 写入 Redo log，同时设置 Redo log 状态为 prepare，再将 Redo log 持久化到磁盘。
- **提交**阶段：将 XA 事务 ID 写入 binlog，将 binlog 持久化到磁盘后，调用 InnoDB 的事务提交接口，此时会将 Redo log 状态设置为 commit。

- 如果两阶段提交过程中出现 MySQL 崩溃怎么办

- MySQL 重启后会按顺序扫描 Redo log 文件，如果某个 Redo log 状态是 prepare，则用该 Redo log 的 XID 去 binlog 中查找是否存在 XID。
- 如果 binlog 中不存在该 XID，说明 Redo log 刷盘成功、binlog 刷盘失败，需要回滚事务。
- 如果 binlog 中存在该 XID，说明 Redo log 和 binlog 都刷盘成功，则提交事务。

## (七) 组提交

- 组提交将多个事务的 binlog 刷盘操作合并为一个，减少磁盘 IO 的次数。
- 组提交将两阶段提交的提交阶段拆分成三个过程，每个阶段各有一个队列，并且对每个队列分别加锁。

- flush 阶段：将多个事务按进入顺序将 binlog cache 写入 page cache。
- sync 阶段：调用 fsync 将这多个 binlog 一次性持久化到磁盘。
- commit 阶段：各个事务按顺序调用 InnoDB 的 commit 接口。

- 在 MySQL5.7 之后，引入 Redo log 组提交

- prepare 阶段不再让各个事务分别执行 Redo log 刷盘，而是推迟到 flush 阶段。

## (八) 脏页刷新

- MySQL 正常刷新。
- 后台线程定时刷盘。
- redo log buffer 满了，会触发脏页刷盘。
- Buffer pool 触发页淘汰时，如果淘汰的是脏页，会将脏页刷盘。

## (九) 内存结构

1. **Change Buffer**：针对非唯一二级索引页，在执行DML语句时，如果数据不在 Buffer Pool 中，不会直接操作磁盘，而是存储在 Change Buffer 中，后面数据被读取时，会将数据合并到 Buffer Pool 中，再将合并后的数据刷新到磁盘中。

## (十) 后台线程

1. **Master Thread**：负责调度线程和将缓冲池中的数据刷新到磁盘中。
2. **IO Thread**：InnoDB 使用 AIO 来处理 IO 请求。

|   |   |   |
|---|---|---|
|线程类型|默认个数|职责|
|Read thread|4|负责读操作|
|Write thread|4|负责写操作|
|Log thread|1|负责将日志缓冲区刷新到磁盘|
|Insert buffer thread|1|负责将写缓冲区内容刷新到磁盘|

3. **Purge Thread**：用于回收事务已经提交了的Undo log。
4. **Page Cleaner Thread**：协助 Master Thread 刷新脏页到磁盘。

# 七、索引

|   |   |
|---|---|
|B+树|一个节点对应一个数据页。非叶节点存储主键+子节点指针；叶子节点存储实际数据行。|
|Hash|MySQL中 Memory 支持 hash 索引，只支持精确查询（如=、in），不支持范围查询（如>、between）。InnoDB 支持自适应 hash 功能，用于优化对 Buffer Pool 数据的查询。|
|R-tree|空间索引是 MyISAM 引擎的一个特殊索引类型，主要用于地理空间数据类型，通常使用较少。|
|Full-text|是一种通过建立倒排索引，快速匹配文档的方式。类似于Lucene、Solr、ES。|

## (一) B+树

- B+树中每一个节点对应一个数据页，其中非叶节点存储主键+子节点指针；叶子节点存储实际用户记录。
- 所有节点按照索引键大小排序，叶子节点通过页头的指针构成双向链表，便于范围查询。

### 1. 为什么使用 B+树？

- 范围查询更加方便；
- 支持排序，B+树根据关键字排序；
- 非叶节点只存储索引，不存储实际数据，一个页存储的索引更多，也可以提高缓存命中率。

### 2. 为什么不用跳表/B 树？

## (二) 索引分类

|   |   |   |
|---|---|---|
|索引分类|数量|说明|
|普通索引|多个|快速定位特定数据。|
|主键索引 **PRIMARY**|唯一|针对于表中主键创建的索引，默认自动创建。|
|唯一索引 **UNIQUE**|多个|避免同一个表中某个字段的值重复。会自动在unique字段上创建唯一索引。|
|前缀索引|多个|在字符类型的字段的前几个字符上建立索引|
|全文索引 **FULLTEXT**|多个|全文索引查找的是文本中的关键词，而不是比较索引中的值|

### 1. 聚簇索引 Clustered Index

- 聚簇索引的叶子节点存储真实用户记录，表的所有用户记录都存储聚簇索引中。因为数据物理层面只需要保留一份，所以每张表一定有且仅有**唯一**的聚簇索引。

- 如果存在主键，**主键**索引就是聚集索引，不可能用其他索引作为主键。
- 如果没有主键，将第一个**唯一非空**列作为聚集索引。
- 如果没有主键，也没有合适的唯一索引，InnoDB 会自动生成一个 6 字节的隐藏列 **row_id** 作为聚集索引。
- 在 8.0.30 版本后，如果没有主键，且开启`sql_generate_invisible_primary_key`（GIPK）特性，即使存在唯一非空索引，也会生成 **row_id**作为主键。

### 2. 二级索引 Secondary Index

- 索引和数据分开存储，索引结构的叶子节点中存储对应的主键值。
- 每张表可以有多个二级索引。
- **回表查询**：先在二级索引中查找数据，利用主键值在聚簇索引中获取数据。

## (三) 索引使用

```SQL
# 创建 唯一、全文、常规索引、前缀索引。
CREATE [UNIQUE | FULLTEXT] INDEX idxName ON tableName(col1, col2(3) ...);
SHOW INDEX FROM tableName;									# 查看索引。
DROP INDEX idxName ON tableName;							# 删除索引。
SELECT * FROM tableName use index(idxName) where ...;		# 建议使用索引。
SELECT * FROM tableName ignore index(idxName) where ...;	# 忽略索引。
SELECT * FROM tableName force index(idxName) where ...;		# 强制使用索引。
```

### 1. 最左前缀法则

- 联合索引中，查询需要从联合索引最左边的列开始，并且不跳过索引中的列。如果跳过某一列，右边列的索引都会失效。

### 2. 范围查询

- 联合索引中，使用范围查询（>、<）的列的右侧的列索引失效。
- 当范围查询为（>=、<=）时，在该列取 = 的情况下，不会导致该列右边的列索引失效；其他情况还是会失效。
- 当范围查询使用 between ... and 时，因为包含左右边界所以类似情况二。

### 3. 索引失效

1. **索引列运算**

- 在索引列上进行计算、函数、类型转换，索引会失效。

2. **字符串不加引号**

- 字符串类型的字段在比较时不加引号，会导致索引失效。字符串不加引号会报错，所以不加引号的字符串只能是数字。但是条件中的数字不会被转换为数字，而是通过隐式转换将索引中的字符串开头的数字部分转换为数值进行比较。

3. **模糊查询**

- 尾部模糊查询，索引不会失效；头部模糊查询，索引失效。

4. **or 条件**

- 用 or 连接的条件，如果有任何一列没有索引，则所有的索引都不会生效。

5. **数据分布**

- 如果使用索引比全表扫描慢，就会放弃使用索引。

### 4. 覆盖索引

- 查询使用了二级索引，并且需要返回的列在该索引中（**索引中的列+主键**）能够全部找到，就不需要回表查询。

### 5. 索引下推

- Extra 出现了 using index condition pushdown 说明使用了索引下推。
- 对于一个联合索引，如果左侧列导致右侧列索引失效。在引擎层提前过滤无效索引，减少回表并且无效索引不用返回 Server 层检查，提高查询的效率。

- Server 层调用 API 定位到满足查询条件的第一条二级索引记录；
- 存储引擎定位到二级索引后，先不执行回表操作，而是先判断一下该索引中包含的列的条件是否成立。如果条件不成立，则直接跳过该二级索引。如果成立，则执行回表操作，将完整记录返回给 Server 层。
- Server 层再判断其他的查询条件是否成立，如果成立则将其发送给客户端；否则跳过该记录，然后向存储引擎索要下一条记录。

### 6. 前缀索引

- 当字段类型为较长的字符串时（char、varchar、text、longtext等），会导致索引变得很大，查询时需要大量的磁盘IO。此时可以只针对字符串的前缀建立索引，节约空间，提高索引效率。

```SQL
create index idxName on tableName(column(n));	# 对某列建立长度为 n 的索引。
```

- **索引选择性/区分度**：选择性指不重复的索引值和数据表记录总数的比值，选择性越高查询效率越高，唯一索引的选择性是1。
- **前缀索引长度**：兼顾索引选择性和索引长度选择。

## (四) 索引设计原则

1. 针对于数据量较大，且查询比较频繁的表建立索引。
2. 针对于常作为查询条件（where）、排序（order by）、分组（group by）操作的字段建立联合索引。
3. 尽量选择区分度高的列作为索引，尽量建立唯一索引，区分度越高，使用索引的效率越高。
4. 如果是字符串类型的字段，字段的长度较长，可以针对于字段的特点，建立前缀索引。
5. 尽量使用联合索引，减少单列索引，查询时，联合索引很多时候可以覆盖索引，节省存储空间，避免回表，提高查询效率。
6. 主键最好是自增的，这样每次插入新数据都不用移动旧数据。
7. 如果索引列不能存储 NULL 值，必须使用 NOT NULL 约束它。当优化器知道每列是否包含NULL值时，它可以更好地确定哪个索引最有效地用于查询。
8. 要控制索引的数量，索引并不是多多益善，索引越多，维护索引结构的代价也就越大，会影响增删改的效率。

## (五) count() 效率/优化

- count() 统计指定字段上不为 NULL 的行数。
- 效率：count(字段) < count(主键) < count(1) ≈ count(*)

|   |   |
|---|---|
||说明|
|count(key)|使用索引遍历全表，把每行的 key 取出来交给 Server 层判断是否为 null，按行进行累加|
|count(字段)|一定会全表扫描。①有 not null 约束：将每行字段值取出交给服务层，按行进行累加。  <br>②没有 not null 约束：将每行字段值取出交给服务层，服务层判断是否为null后，累加计数。|
|count(1)|遍历整张表，但不取值。服务层对于返回的每一行，放一个数字“1”进去，直接按行进行累加。|
|count(*)|会被优化为 count(0)，不用判断是否为 NULL，不需要取出具体的字段。Server 层直接按行累加。|

## (六) limit 分页问题

`limit size`等价于`limit 0 size`。

### 1. 基于主键的 limit

- `limit offset size`innodb 会从**聚簇索引**中获取并向 Server 层返回 **offset+size 条完整记录**，然后丢弃前 offset 个数据并保留最后 size 条数据。
- 可以通过**子查询**的方式，获取第 offset+1 的行的 id 值，然后查询大于等于该值的 size 条数据。子查询只会返回**一条记录**的 id 到 server，然后再从主键索引中快速定位并向后获取 10 条记录。

```SQL
select * from page 
	where id >=(select id from page order by id limit 6000000, 1) 
	order by id 
	limit 10;
```

### 2. 基于二级索引的 limit

- 当 offset 较小或 =0 时，会先使用二级索引然后回表。首先查二级索引将 **offset+size 个主键 id** 返回给 Server 层，然后丢弃前 offset 个 id 并保留最后 size 条 id，用这些 id 回表。
- 当 offset 很大时，优化器觉得回表次数太多就会变成全表扫描。
- **子查询 + 连表**：可以先子查询得到中间结果的 id，再通过连表的方式查询整行数据。

```SQL
select * from page t1, 
		(select id from page order by user_name limit 6000000, 100) t2 
	WHERE t1.id = t2.id;
```

### 3. 深分页问题

- **游标**：可以用上一批数据中最大的主键 id 作为条件查询这一批数据。
- **子查询**：

# 八、SQL 优化

## (一) Explain 关键字

- 常用字段

|   |   |
|---|---|
|type|表示扫描数据的方式。|
|possible_keys|表示可能用到的索引。|
|key|表示实际用的索引，如果这一项为 NULL，说明没有使用索引 。|
|key_len|表示实际使用的索引列长度，可以判断使用了哪些列。|
|rows|表示扫描的数据行数。|

- type 字段

|   |   |
|---|---|
|all|全表扫描。|
|index|全索引扫描。|
|range|使用索引范围扫描。|
|ref|非唯一索引扫描。|
|eq_ref|主键索引/唯一索引扫描，常用于多表联合查询。|
|const|结果只有一条的主键扫描或者唯一索引扫描，常用于主键或唯一索引的常量查询。|

- Extra 字段

|   |   |
|---|---|
|Using filesort|使用 group by 操作且无法使用索引进行排序分组，必须使用额外的排序算法，甚至是文件排序。|
|Using temporary|使用临时表保存的中间结果，order by 或 group by。|
|Using index|索引覆盖|

## (二) insert 优化

### 1. 插入数据

- 如果一次性插入多条数据，可以从三个方面优化：①批量插入；②手动控制事务；③按主键顺序插入。

### 2. 大批量数据

- 对于大批量数据，可以使用 load 语句插入，并且主键顺序插入性能高于乱序插入。

```SQL
-- 客户端连接服务端时，加上参数 -–local-infile
mysql –-local-infile -u root -p
-- 设置全局参数local_infile为1，开启从本地加载文件导入数据的开关
set global local_infile = 1;
-- 执行load指令将准备好的数据，加载到表结构中
load data local infile '/root/sql1.log' into table tb_user fields
terminated by ',' lines terminated by '\n' ;
```

## (三) 主键优化

1. 索引组织表

- InnoDB 中，表数据都是根据主键顺序组织存放的。行数据存储页中，页之间通过指针连接。

2. 页分裂

- 当一个页已经存满，并且该页后方的页非空时，想要向该页插入数据，此时就会开辟一个新的页，然后将该页后一半数据移到新页中，并将需要的数据也插入到新页中。

3. 页合并

- 当一个页中的数据被删除到合并阈值（默认页的一半）时，InnoDB 会寻找前后方的页，查看是否可以将两个页合并。

4. 主键索引设计

- 尽量降低主键长度。
- 插入数据，尽量按主键顺序插入，使用自增主键。
- 避免对主键的修改。

## (四) order by 优化

### 1. MySQL 排序方式

- **Using filesort**：通过索引或全表扫描，读取满足条件的数据行，然后在排序缓冲区sort buffer 中完成排序操作，所有不是通过有序索引直接返回排序结果的都叫 FileSort 排序。
- **Using index**：通过有序索引顺序扫描直接返回有序数据，不需要额外排序，操作效率高。

### 2. order by 优化原则

- 根据排序字段建立索引，联合索引也遵循最左前缀法则。
- 尽量使用覆盖索引。
- 多字段排序，如果既有升序又有降序，应该在创建联合索引时指定索引排序规则。

## (五) group by 优化

- 根据分组字段建立索引，联合索引同样遵循最左前缀法则。

# 九、MySQL 集群

## (一) 主从复制

- 主库在事务提交时，将数据变化写入 binlog 中。
- 从库启动一个 IO 线程连接主库的 log dump 线程，读取主库的 binlog，并写在 relay log 中，向主库返回复制成功的响应。
- 从库读取 relay log 并更新自己的数据，实现主从一致性。

### 1. 主从复制的模型

- 同步复制：主库必须所有从库复制成功的响应，才能返回结果。性能和可用性很差。
- 异步复制：默认。主库的事务线程不等待 binlog 复制到从库，可以直接给客户端返回结果。
- 半同步复制：主库只需要等待一部分从库响应，就可以向客户端返回结果。

## (二) MySQL 集群

# 十、分库分表