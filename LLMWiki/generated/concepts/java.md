# Java、集合与 Spring

自动主题地图：按标题/章节中的术语归组。关联仅表示主题邻近，不表示技术等价。

路由词：HashMap、集合、Spring、Bean、AOP、IOC、反射

## 来源入口

### [Java 集合](../notes/d_d407c5c86714794b939abcf9.md)

来源：`02-Java 后端/Java 集合.md` · SHA-256 `b3fdb2e3a407`

- L110-L111 · 三、双列集合 Map > (二) HashMap：无序、不重复、无索引
- L112-L116 · 三、双列集合 Map > (二) HashMap：无序、不重复、无索引 > 1. 底层：哈希表

  摘录（原文）：

  ```text
  - JDK7：数组+链表，新元素存入数组即链表头，老元素后移（头插法）。
  ```

- L117-L125 · 三、双列集合 Map > (二) HashMap：无序、不重复、无索引 > 2. 添加元素 put()/putVal()

  摘录（原文）：

  ```text
  - 如果 table 为 null（第一次添加）或长度为 0，调用 **resize()**。
  ```

- L126-L141 · 三、双列集合 Map > (二) HashMap：无序、不重复、无索引 > 3. 扩容 resize()

  摘录（原文）：

  ```text
  - 第一次添加数据
  ```

- 其余 47 个相关章节见来源卡片。

### [Spring](../notes/d_aeac005e2a534eb58b3eeb1d.md)

来源：`02-Java 后端/Spring.md` · SHA-256 `19e910c663fe`

- L3-L4 · 一、Spring 框架 > (一) IOC
- L5-L8 · 一、Spring 框架 > (一) IOC > 1. **控制反转（Inversion of Control，IOC）**

  摘录（原文）：

  ```text
  - IOC 指开发者不通过 new 手动创建对象或维护依赖关系，而是由框架负责创建对象、依赖管理。
  ```

- L9-L16 · 一、Spring 框架 > (一) IOC > 2. 依赖注入（Dependency Injection，DI）

  摘录（原文）：

  ```text
  - DI 是实现 IOC 的一种方式。开发者只需要用配置文件或注解声明对象的依赖关系，Spring 容器会自动创建对象并注入当前对象依赖的对象。
  ```

- L17-L22 · 一、Spring 框架 > (一) IOC > 3. Spring 容器（Container）

  摘录（原文）：

  ```text
  - 容器是 IOC 的载体，负责对象的创建、依赖注入、生命周期管理等操作。
  ```

- 其余 16 个相关章节见来源卡片。

### [Java 基础](../notes/d_1c6c8977e2110f25f6baa9de.md)

来源：`02-Java 后端/Java 基础.md` · SHA-256 `f551310fcb69`

- L146-L151 · 二、面向对象 > (六) 反射

  摘录（原文）：

  ```text
  - 在运行状态中，对于任意一个类或对象，都能用编程方式获取或调用它的**字段**、**方法**和**构造器**。
  ```

- L152-L156 · 二、面向对象 > (六) 反射 > 1. Class 对象

  摘录（原文）：

  ```text
  - 每个类在 JVM 中都有且仅有一个 Class 对象，它存储了类的所有元数据：类名、修饰符、父类、接口数组、字段数组、方法数组、构造器数组等。
  ```

- L157-L194 · 二、面向对象 > (六) 反射 > 2. 获取和使用 Class 对象

  摘录（原文）：

  ```text
  1. 获取 Class 对象
  ```

- L195-L218 · 二、面向对象 > (六) 反射 > 3. 元数据对象 Constructor、Field、Method

  摘录（原文）：

  ```text
  1. Constructor
  ```

- 其余 1 个相关章节见来源卡片。

## 相邻主题

- [JVM、内存与垃圾回收](runtime.md)
- [线程、锁与并发控制](concurrency.md)

## 检索入口

```powershell
python LLMWiki/wiki.py search "HashMap"
```
