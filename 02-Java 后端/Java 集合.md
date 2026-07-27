<img src="00-resource/images/Java 集合.png" style="zoom:75%;">

# 一、迭代器 Iterator

- 接口 Iterator 的实现类对象，可以**遍历**集合，在遍历集合的过程中可以通过迭代器**删除、修改**元素。
- Iterator 遍历集合时不依赖索引，只能**单向遍历**，遍历完后 cursor 不会自动复位。
- Iterator 在没有元素的位置强行 **next()**，会报 `NoSuchElementException`。

# 二、单列集合 Collection

## (一) 遍历

- **Iterator**：在遍历集合时可以安全地删除元素。
- **增强 for**（for-each）：增强 for 可以遍历 Collection 和数组。其中集合使用迭代器遍历，数组使用索引遍历。
- **forEach：**Iterable 接口的默认方法，默认使用增强 for 实现，需要传入一个 Consumer。

## (二) List：有序、可重复、有索引

### 1. 遍历 List

① Iterator；② ListIterator；③ 增强 for；④ forEach；⑤ 普通 for。

#### 一、列表迭代器 ListIterator

- 可以正向遍历，也能反向遍历，游标默认初始化。
- ListIterator 在遍历 List 时，可以**增删改**元素（ add()、remove()、set() ）。

#### 二、List 遍历的最佳实践

- 简单读取：增强 for、普通 for（只适合实现了 RandomAccess 接口的类如 ArrayList、Vector）。
- 复杂操作：stream 流。
- 修改删除：Iterator、ListIterator。

### 2. List 与数组

#### 一、数组转 List

- List.of(arr)：不可变集合，传递基本数据类型数组会被当作一个引用对象处理。
- Arrays.stream(arr)：基本数据类型数组需要先用 boxed() 装箱。
- Arrays.asList(arr)：列表和原数组共用底层数组，修改会互相影响。

#### 二、List 转数组

- list.toArray()/list.stream().toArray()：无参构造返回 Object[]，有参构造指定数组类型。

### 3. ArrayList

- **底层**：用 Object 数组 elementData 存储实际元素。

```
transient Object[] elementData;
```

- **创建**

- **空参构造**：使用静态空数组为 elementDate 赋值，size = 0。
- **有参构造**：使用初值 0 或者空集合初始化，则使用另一个静态空数组为 elementDate 赋值，size = 0；如果初值不为 0 或者集合非空，则使用实际长度创建数组并赋值给 elementDate。

- **扩容**

- 空参构造的初次扩容至少扩容到 10。
- 有参构造的扩容、空参构造的非初次扩容，如果一次增加一个元素，那么每次创建新数组，长度为原来的**1.5倍**；如果一次增加多个元素，且**1.5倍**不够，以**实际为准**。将原数组用`Arrays.copyOf` 复制到新数组。

### 4. LinkedList

- 底层：带头、尾指针的双链表，默认使用尾插法。

### 5. Vector

- Vector 的所有方法都使用 synchronized 关键字实现线程同步，是线程安全的。
- Vector 的扩容默认扩容 1 倍，而 ArrayList 默认扩容 50%。
- 随机读/写性能：ArrayList > Vector > LinkedList。
- 默认写性能：LinkedList > ArrayList > Vector。

## (三) Set：无序、唯一、无索引

### 1. HashSet：无序、不重复、无索引

- 基于 **HashMap** 实现，HashSet 中持有一个 HashMap 对象，HashSet 中的元素作为 HashMap 的 Key 存储，所有 value 都存储同一个静态 Object 常量 PRESENT。

### 2. LinkedHashSet：有序、不重复、无索引

- 继承自 HashSet，基于 **LinkedHashMap** 实现，通过双链表记录元素的插入顺序。

### 3. TreeSet：可排序、不重复、无索引

- 基于 **TreeMap** 实现，使用红黑树实现存储和排序。

## (四) Queue：有序、可重复

- 双端队列的实际实现，可以当作栈使用 (push、pop、peek)，也可以当作队列使用 (add、poll、peek)

### 1. Deque

- 双向队列，既可以当作栈用，也可以当作队列使用。
- **ArrayDeque**：底层是数组。
- LinkedList：

### 2. PriorityQueue

- 优先级队列，默认是小根堆。

# 三、双列集合 Map

## (一) 遍历

- **entrySet()**/**keySet()**/**values()**：①iterator()；②增强for；③forEach()。
- map.**forEach()**。

## (二) HashMap：无序、不重复、无索引

### 1. 底层：哈希表

- JDK7：数组+链表，新元素存入数组即链表头，老元素后移（头插法）。
- JDK8：数组+链表+红黑树，新元素插入到链表尾（尾插法）或者红黑树。

### 2. 添加元素 put()/putVal()

- 如果 table 为 null（第一次添加）或长度为 0，调用 **resize()**。
- 利用数组 table 的长度 **length** 和 key 的哈希值即 **hash(key)**，计算在数组中的下标。
- 如果目标位置 =null，用键值对创建 Node 并直接加入数组。
- 如果目标位置 !=null，且不存在 key.equals() 为 true 的节点，则将键值对插入红黑树或链表尾部，并且判断如果插入此键值对后**链表长度 >=8 且数组长度 >=64**，则将链表转换为**红黑树**，红黑树根据 key 的哈希值排序。
- 如果目标位置 !=null，且存在 key 相等的节点，**覆盖**并返回旧的 value。
- 如果 map 中元素数量 size 达到了扩容窗口 threshold，则调用 resize()。

### 3. 扩容 resize()

- 第一次添加数据

- **有参构造**：创建 HashMap 时，初始长度会被调整大于等于初始长度的最小 2 的幂次方。按照调整后的初始长度、加载因子不变来创建数组 table。
- **无参构造**：默认创建一个长度 **16**、加载因子 **0.75** 的数组 table。

- 后续添加数据

- 如果数组长度大于等于 2^30，则直接返回旧数组；否则按照旧数组长度 2 倍创建新数组。
- 扩容后

- 如果旧数组该索引只有一个元素，则根据新数组长度和 key 的哈希值计算新的下标。
- 如果不止一个元素，则根据`e.hash & oldCap==0`即高位是否为 0，判断要么插入新数组的原索引，要么插入新数组的新索引（原索引+扩容量）。
- 如果红黑树拆分后树中结点数量 <=6，则将红黑树转换为链表。

### 4. 哈希

- HashMap 依赖 key 的 hashCode()、equals() 保证 key 唯一，如果 key 是自定义类必须重写hashCode()、equals()。
- HashMap 支持 null 作为 key，并且 hash() 函数中 null 计算结果为 0，最终下标也是 0。

### 5. 为什么不直接使用 hashCode() 作为元素在数组中的下标？

1. hashCode() 返回值是 **int 类型**，取值范围为 -(1<<31)~(1<<31 - 1)，但是 HashMap 的存储范围是 16~2^30，且多数情况下远低于最大值，hashCode() 的结果就可能导致越界。
2. hash() 方法让 hashCode() 低 16 位与高 16 位进行了**异或**运算，然后通过`(n-1) & hash` 计算下标。两次扰动使得分布均匀，降低了哈希碰撞的概率，保证了下标不会越界，并且位运算的效率高。

## (三) LinkedHashMap：有序、不重复、无索引

- 继承自 HashMap，LinkedHashMap 中的元素额外增加前向指针和后向指针，即所有元素还构成双链表。
- LinkedHashMap 的双链表默认按照插入顺序维护，也可以通过创建对象设置参数 accessOrder 按照访问顺序维护即最新插入或最近访问的在链表头。

## (四) TreeMap：可排序、不重复、无索引

### 1. 底层：红黑树，对键进行排序

#### 1. 左根右、根叶黑、不红红、黑路同

- 红黑树是一个二叉排序树，其中每个结点要么是红色，要么是黑色。
- 根节点是黑色，叶节点（Nil结点）是黑色。
- 不存在两个相邻红节点。
- 对任何节点，从该节点到其后代的叶节点的简单路径上，黑节点数量都相同。
- 黑高：从任一结点到其后代叶节点的黑节点总数。

#### 2. 红黑树插入

<img src="00-resource/images/红黑树插入.png" style="zoom:50%;">

### 2. 排序

- TreeMap 默认使用自然排序，如果自然排序无法满足要求，可以自定义比较器实现排序。
- TreeMap 不使用 hashCode()、equals()，不需要重写。

### 3. key 为自定义类，必须自定义排序规则

1. 自然排序：自定义类实现 **Comparable** 接口，重写 **compareTo()** 方法。
2. 比较器：创建 TreeMap 对象时，可以传递 **Comparator** 对象，重写 **compare()** 方法。
3. TreeMap 默认使用自然排序，如果自然排序无法满足要求，必须使用比较器实现排序。

## (五) HashTable

- HashTable 的所有方法都使用 synchronized 关键字实现线程同步，是线程安全的。
- HashMap 默认初始容量为**16**，默认扩容**1倍**；HashTable 默认容量**11**，默认扩容 **2n+1**。
- 给定初始容量时，HashMap 会扩充到2的幂次方，HashTable 直接使用给定初始容量。

# 四、Java集合的快速失败机制 Fail-Fast

- Fail-Fast 机制是 Java 集合的一种错误检测机制，用来检测集合在**多线程下的并发修改**或**单线程迭代时修改集合结构**，并快速抛出异常`**ConcurrentModificationException**`。
- 所有 Collection 都采用的是快速失败机制，不能在多线程下发生并发修改。
- 集合类会维护一个修改计数器 **modCount** 记录**集合变化**的次数，使用集合自身的方法修改集合会导致 modCount 自增。
- 在集合遍历过程中或其它操作中，首先记录当前 modCount 为 **expectedModCount**，然后检查 modCount 是否与 expectedModCount 相等，如果不相等就会抛出异常。

# 五、怎么在遍历集合时安全的修改/删除元素？

1. 迭代器
2. 倒数普通 for：核心就是正确的处理索引/下标。
3. 用并发安全集合
4. 用 stream 的 filter：简单高效、安全
5. List 可以使用 removeIf() 方法删除所有满足条件的元素。

# 六、线程安全的集合类

## (一) 遗留的线程安全集合

- Vector、HashTable 使用 synchronized 修饰方法，高并发场景下性能低，不推荐使用。

- **Collections** 提供的方法可以将普通的集合类对象转换为线程安全的对象，其实现原理是在同步代码块中调用原集合类的方法，高并发场景下性能较低。

```
synchronizedCollection();
synchronizedList();
synchronizedSet()/synchronizedNavigableSet()/synchronizedSortedSet();
synchronizedMap()/synchronizedNavigableMap()/synchronizedSortedMap();
```

## (二) 不可变集合

- 不可变集合定义完成后不可以修改、添加、删除。
- **List/Set.of(T... elements)**：可以传递多个参数构建不可变集合。
- Map

- **of**() 方法最多传递10个键和10个值。
- **ofEntries**(Entry<? extends K, ? extends V>... entries) 方法可以传递多个entry。
- **copyOf**(Map<? extends K, ? extends V> map) 方法传递一个Map对象。

## (三) JUC 线程安全集合类

### 1. Concurrent

- 很多操作使用 CAS 实现，可以提供较高吞吐量。但是集合遍历、大小、读取等一致性较弱。

#### 一、ConcurrentHashMap

- 支持高并发、高吞吐量的线程安全的 HashMap，ConcurrentHashMap **不允许键为 null**。

1. **JDK7**

- 采用**数组+链表**实现，使用**分段锁**进行并发控制。
- 数组又分为大数组 **Segment[]** 和小数组 **HashEntry[]**，ConcurrentHashMap 默认分为 16 个 Segment，每个 Segment 又包含一个 HashEntry[]，每一个 HashEntry 是一个链表，链表中保存实际元素。
- 每一个分段有个 Segment 锁，**Segment** 锁继承自 **ReentrantLock**，当线程对数据进行修改时，必须首先获得对应 Segment 的分段锁。不同分段可以并发访问。

2. **JDK8**

- 采用**数组+链表+红黑树**实现，用 **synchronized** 或 **volatile+CAS** 实现并发控制。锁粒度细化到数组元素即桶。

3. **添加元素**

- 如果 table 为 null（第一次添加）或长度为 0，调用 **initTable()** 通过 CAS 操作试图对 table 初始化。
- 利用 table 的长度和 key 的哈希，计算在数组中的下标`(n-1) & hash`。
- 如果目标位置 = null，则通过 CAS 创建 Node 并加入数组。
- 如果目标位置头节点哈希值为 **MOVED** 即 **-1**，则说明正在扩容，当前线程参与扩容。扩容完进入下一轮循环，重新计算下标。当红黑树中节点<=6 时，退化为链表。
- 使用 synchronized 对**链表头**或**树根**加锁，遍历链表或红黑树中的元素，替换或者新增节点，并判断如果插入此键值对后**链表长度 >=8 且数组长度 >=64**，则将链表转换为**红黑树**。

4. **size**

- size 计算都发生在 put、remove 等改变集合元素的操作中。
- 没有竞争时，向 baseCount 累加计数。有竞争时，创建 counterCells 数组，每个线程向一个 cell 累加计数。

- counterCells 初始有 2 个 cell。

5. **扩容**

- ForwardingNode 表示当前桶已经迁移，

#### 二、ConcurrentLinkedQueue/ConcurrentLinkedDeque

- 使用 CAS 操作实现了两把乐观锁，可以允许一个消费者和一个生产者同时执行。

### 2. Blocking

- 大部分实现都基于锁，并且提供依赖阻塞的方法。

#### 一、ArrayBlockingQueue

- 基于数组实现的有界队列，数组创建后容量不可变。
- 使用一把锁控制读写，不支持读写并发。

#### 二、SynchronousQueue

- 不存储实际元素，元素在生产者和消费者之间直接转发。每一个插入/取出操作都必须等待对应的取出/插入操作。

#### 三、LinkedBlockingQueue

- 带头节点的链表，具有头指针和尾指针。

1. 加锁

- 有两把 ReentrantLock 锁，分别用来对头指针、尾指针加锁，可以允许一个生产者、一个消费者并行执行；但是消费者、生产者之间仍然串行执行。

2. 添加

- **put()** 是阻塞方法，当队列已满时，会阻塞生产者。
- **offer()** 是非阻塞方法，当队列已满时，会直接返回 false。

3. 取出

- **take()** 是阻塞方法，当队列已空时，会阻塞消费者。
- **poll()** 是非阻塞方法，当队列已空时，会直接返回 null。

### 3. CopyOnWrite（CopyOnWriteArrayList）

- 使用 volatile 修饰数组，当前线程对数组重新赋值后，其他线程可以及时感知到。
- 读操作直接返回结果；
- 写操作会加 synchronized 锁，首先复制原数组，在新数组上插入或修改元素，最后用新数组替换旧数组。