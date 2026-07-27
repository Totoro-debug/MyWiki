# 一、数据类型

## (一) 基本数据类型

| 类型    | 内存 | 默认值   |
| ------- | ---- | -------- |
| long    | 8B   | 0L       |
| int     | 4B   | 0        |
| short   | 2B   | 0        |
| byte    | 1B   | 0        |
| char    | 2B   | '\u0000' |
| float   | 4B   | 0.0F     |
| double  | 8B   | 0.0D     |
| boolean | 1B   | false    |
- `boolean`原理上只需要 1bit 即可表示布尔值，但是因为 Java 规范中没有强制规定，所以实际依赖于 JVM 的实现，一般认为是 1B。

## (二) 包装类

- 与基本数据类型对应的类。

### 1. 自动装箱、自动拆箱

- 即基本类型和包装类型之间会自动互相转换，底层其实是调用了 `Integer.valueOf()` 和 `Integer.intValue()`。

### 2. 自动拆箱的 NPE 风险

- 在业务中，返回值不建议使用基本数据类型，因为数据库的查询结果可能是 null 即没有结果，如果使用基本数据类型就会发生拆箱，拆箱会调用 `Integer.intValue()` 方法导致`NullPointerException`。
- 三目运算符中，如果基本数据类型和包装类混用就会发生拆箱，最后导致 NPE 问题。

### 3. 包装类的常量池缓存

- `Byte`、`Short`、`Integer`、`Long` 通过静态内部类缓存了值在 **[-128,127]** 之间的实例。
- `Character` 通过静态内部类缓存了值在 **[0,127]** 之间的字符对象。
- `Boolean` 直接缓存 **True** 和 **False** 两个对象。

# 二、面向对象

## (一) 面向对象三大特性

- **封装**：将数据和方法结合在一起，并尽可能隐藏内部实现细节，对外提供公共访问方式，提高安全性和模块化。
- **继承**：子类可以继承父类的属性和方法，并可以扩展或重写。Java只支持单继承，但可以通过接口实现多继承效果。
- **多态**：同一操作作用于不同对象，可以有不同的解释和结果。包括编译时多态（方法重载）和运行时多态（方法重写）。

## (二) 继承

1. **构造方法**：子类不能继承构造方法，子类构造方法会默认调用父类无参构造。
2. **静态变量**：可以继承 public、protected、同包default，可以隐藏。
3. **静态方法**：可以继承 public、protected、同包default，不能重写，但是可以隐藏。
4. **成员变量**：可以拥有父类所有成员变量，但是只能访问 public、protected、同包default。
5. **成员方法**：可以继承父类非priavte、非final成员方法，可以重写。
6. this 与 super

- 一个类在内存中，首先初始化父类的字段和方法等，然后进一步初始化子类的成员，super指向属于父类的内存区域，this指向属于子类的内存区域。

1. Java 为什么不支持多继承？

- 菱形继承问题：方法二义性、字段重复、构造器调用复杂、维护困难。
- 需求不大，可以通过接口实现特性。

## (三) 重写 Override、隐藏 Hide、重载 Overload

- **Override** 指子类定义与父类有相同名称、相同形参的成员方法。

- 访问权限：不低于父类。
- 返回类型：与父类的返回类型相同或其子类。
- 异常：子类方法可以抛出任何运行时异常，但是不能抛出新的以及更高的编译时异常。如果子类方法产生新的编译时异常，只能捕获处理，不能向上抛出。

- **Overload** 指同一个类中，有名字相同、形参不同的多个方法。
- **static** 方法不能重写，可以隐藏和重载。
- **private** 方法不能重写，可以隐藏和重载。
- **final** 方法**不能重写、隐藏**，可以重载。

### 1. Java 怎么实现重写

- **每个类**在类加载时，JVM 会为其创建一个**虚方法表**，存储在方法区。表中存储了该类所有虚方法（除 private、static、final 以外的实例方法）的实际入口地址。
- **继承与覆盖规则**：

- 先复制父类的虚方法表到子类。
- 如果子类**重写**了父类的某个方法，则用子类方法的地址**覆盖**虚方法表中对应槽位。
- 如果子类新增了方法，则追加到表末尾。

## (四) 多态

### 1. 必要条件

- **继承/实现关系**。
- **方法重写**。
- **向上转型**：父类引用指向子类对象。

### 2. 成员调用

- 成员变量：编译看父类，运行也看父类。
- 成员方法：编译看父类，运行看子类。

### 3. 向下转型

- 父类引用强制转换为子类引用，父类引用实际指向的必须是子类对象，否则报 `ClassCastException`。

## (五) 抽象类与接口

|        | 抽象类                                                       | 接口                                                         |
| ------ | ------------------------------------------------------------ | ------------------------------------------------------------ |
| 继承   | 类只能单继承。                                               | 接口可以多继承，类也可以实现多个接口。                       |
| 字段   | **任意访问**权限的静态变量、成员变量、常量。                 | 只能是 public static final 类常量，必须赋**初值。**          |
| 方法   | **① 任意访问**权限的静态方法、成员方法。② **非 private** 的抽象方法、构造方法。 | ① 抽象方法，默认为 public abstract。② jdk8 开始，可以有 default、static 方法。③ jdk9 开始，可以有 private 方法。 |
| 实现类 | 实现类必须实现所有抽象方法，否则必须定义为抽象类。           | 实现类必须实现所有抽象方法，否则必须定义为抽象类。           |

### 1. 接口的方法

- **抽象方法**：默认 **public abstract** 。
- **默认方法**（jdk8） 

- 如果实现类实现的多个接口存在同名默认方法，实现类要么**重写**该方法，要么通过`**接口.super.方法名()**`指定调用哪个接口的默认方法。

```
default int method(params){……}
```

- **静态方法**（jdk8）

- 静态方法只能通过接口名调用，无法通过实现类对象调用。

```
static int method(params){……}
```

- **私有方法**（jdk9）

- 普通私有方法，给默认方法使用，实现类不能访问。

```java
private returnVal method(params){……}
```

- 静态私有方法，给静态方法使用，实现类不能访问。

```java
private static returnVal method(params){……}
```

### 2. 函数式接口

- 只有一个抽象方法的接口，可以使用 `@FunctionalInterface` 注解进行声明。
- 用于 **lambda** 表达式简化书写。

## (六) 反射

- 在运行状态中，对于任意一个类或对象，都能用编程方式获取或调用它的**字段**、**方法**和**构造器**。
- **运行时类信息访问**：反射允许程序在运行时获取类的完整结构信息：类名、包名、父类、接口、构造器、字段、方法等。
- **动态对象创建**：运行时动态创建对象实例：Class 类的 newInstance() 方法或 Constructor 对象的 newInstance() 方法。

### 1. Class 对象

- 每个类在 JVM 中都有且仅有一个 Class 对象，它存储了类的所有元数据：类名、修饰符、父类、接口数组、字段数组、方法数组、构造器数组等。
- 反射的本质就是操作方法区中的 Class 对象，访问和使用里面的各种元数据。

### 2. 获取和使用 Class 对象

1. 获取 Class 对象

| **方式**                            | **性能** | **类加载**                               |
| ----------------------------------- | -------- | ---------------------------------------- |
| **类名.class**                      | 最高     | 加载但是不立即初始化，使用时才进行初始化 |
| **对象.getClass()**                 | 高       | 创建对象时已经完成了加载、链接、初始化   |
| **Class.forName("全类名")**         | 低       | 立即进行加载、链接、初始化               |
| **ClassLoader.loadClass("全类名")** | 低       | 加载但是不立即初始化                     |

1. 获取 **Constructor** 对象

```java
public Constructor<?>[] getConstructors(); // 所有公共构造方法
public Constructor<?>[] getDeclaredConstructors(); // 所有构造方法
public Constructor<T> getConstructor(Class<?>... parameterTypes); // 指定单个公共构造方法
public Constructor<T> getDeclaredConstructor(Class<?>... parameterTypes); // 指定单个任意构造方法
```

1. 获取 **Field** 对象

```java
public Field<?>[] getFields(); // 该类所有公共字段：包括静态、包括继承，同名字段遵循覆盖规则
public Field<?>[] getDeclaredFields(); // 该类所有字段：包括静态、包括继承，同名字段遵循覆盖规则
public Field getField(String name); // 该类指定单个公共字段
public Field getDeclaredField(String name); // 该类指定单个任意字段
```

1. 获取 **Method** 对象

```java
public Method<?>[] getMethods(); // 该类所有公共方法：包括静态、包括继承
public Method<?>[] getDeclaredMethods(); // 该类所有方法：包括静态、包括继承
public Method getMethod(String name, Class<?>... parameterTypes); // 该类指定单个公共方法
public Method getDeclaredMethod(String name, Class<?>... parameterTypes); // 该类指定单个任意方法
```

### 3. 元数据对象 Constructor、Field、Method

1. Constructor

```java
public int getModifiers();				// 获取修饰符。
public Parameter[] getParameters(); 	// 获取参数列表。
public T newInstance(Object ... initargs);	// 创建一个新实例。
public void setAccessible(boolean flag);	// 设置为true表示抑制访问控制检查。
```

1. Field

```java
public Object get(Object obj);				// 返回指定对象的该字段的值。
public void set(Object obj, Object value);	// 设置指定对象的该字段的值。
```

1. Method

```java
public Object invoke(Object obj, Object... args);	// 用指定对象obj运行该方法，并获取返回值。
```

### 4. 为什么反射慢？

|          | 直接调用           | 反射调用                               |
| -------- | ------------------ | -------------------------------------- |
| JIT 优化 | 方法内联           | JIT 不能进行方法内联                   |
| 方法查找 | 编译时确定方法地址 | 遍历 Method 数组，对比方法名和参数类型 |
| 参数装箱 | 直接将值压栈       | 基本数据类型需要装箱、拆箱             |
| 安全检查 | 编译时检查         | 每次反射调用都要检查（可以跳过检查）   |

## (七) 代理

- 使用代理对象代替真实对象，实现无侵入式地增强对象的功能。
- 代理类默认是不会生成 **.class** 文件的，只在运行时在内存中动态生成字节码文件，但是可以通过参数设置编译时生成字节码文件。

### 1. 静态代理

- 目标类和代理类实现同一个接口，每一个目标类都需要一个单独的代理类。
- 目标对象注入代理类，代理类的方法中调用目标对象的相应方法。

### 2. 动态代理

1.  **JDK 动态代理**

- JDK 动态代理只能代理**接口的实现类**或者**接口**本身，被代理的方法必须是接口中定义的方法。
- JDK 动态代理类是通过**实现接口**，进而实现对被代理方法的增强或拦截，因此只能实现对 **public** 方法的代理。

1. 当动态代理对象调用一个方法时，通过它持有的 InvocationHandler 实现类对象调用 invoke() 方法。
2. invoke() 方法内，使用动态代理对象 proxy 和被调方法的 Method 对象实现了对被代理方法的增强或拦截。

- **InvocationHandler** 

- 实现接口 InvocationHandler，实现 invoke() 方法以实现对被代理方法的增强或者拦截。

```
public Object invoke(    Object proxy, 	// 动态代理对象    Method method, 	// 被调方法的Method对象    Object[] args)	// 被调方法的参数
```

- **Proxy**

- 使用 newProxyInstance() 方法创建动态代理对象。

```
public static Object newProxyInstance(    ClassLoader loader, 	// 类加载器，一般用被代理类对象/接口的类加载器                              Class<?>[] interfaces,	// 需要被代理的接口    InvocationHandler h);	// InvocationHandler 的自定义实现类对象
```

1. **CGLIB 动态代理**

- CGLIB 通过生成**被代理类的子类**拦截被代理类的方法调用，不能代理无法继承的类和无法继承的方法（final类、final方法、private方法），被代理方法会被动态代理类重写。
- 当动态代理对象调用被拦截方法时

- 被重写后的方法首先调用它持有的 MethodInterceptor 实现类对象的 intercept() 方法。
- intercept() 方法内，对被代理方法进行拦截或增强，然后使用被代理方法的代理对象 proxy 和被代理对象 obj 调用 invokeSuper() 方法。
- invokeSuper() 方法会调用父类中原本的被代理方法。

- **MethodInterceptor**

- 实现接口 MethodInterceptor，实现 intercept() 方法以实现对被代理方法的增强或拦截。

```
public Object intercept(    Object obj, 						// 被代理对象    java.lang.reflect.Method method,	// 被拦截方法的Method对象    Object[] args,						// 方法实参    MethodProxy proxy					// 被拦截方法的代理对象 ) throws Throwable;
```

- **Enhancer**

- 使用 create() 方法创建动态代理对象。

```
public static Object create(    Class type,			// 被代理类Class对象    Callback callback	// 方法拦截器，一般是 MethodInterceptor 的自定义实现类对象 );
```

## (八) 内部类

1. **静态内部类**

- 实例化：可以直接创建内部类对象，不依赖外部类对象。

```
Outter.Inner inner = new Outter.Inner(); 
```

- 外部类成员

- 只能访问外部类的静态变量、静态方法。若想访问外部类非静态成员，必须先创建外部类对象。
- 不能直接访问外部类私有成员，必须先创建外部类对象。

- 内部类成员：可以定义静态成员。

```
Outter.Inner.var/method();
```

1. **匿名内部类**（成员、方法内）

- 实例化：实际上创建了一个抽象类/接口的实现类对象。

```
new 抽象类/接口(){    方法重写; };
```

- 外部类成员：可以访问包括private的成员变量、成员方法。
- 内部类成员：不能定义静态成员。

1. 成员内部类（成员）

- 实例化：必须先创建外部类对象。

```
Outter.Inner inner = new Outter().new Inner(); 
```

- 外部类成员：可以访问所有成员（private、static），如果内部类成员与外部类成员同名，访问外部类成员必须使用`Outter.this.var/method()`。
- 内部类成员：不能定义静态成员。

1. 局部内部类

- 实例化：方法内创建内部类对象。
- 外部类成员：可以直接访问外部类成员。

# 三、String

- String 是一个典型的不可变类，天然**线程安全**。
- String 实现了 Serializable 接口支持序列化，实现了 Comparable 接口支持排序。

### 1. 不可变类

- **final** 类：不允许继承，防止子类破坏 String 的特性。
- **private final** 数组：不允许修改 String 对象中字节数组的引用，并且不对外提供接口修改数据。
- 赋值、拼接、replace 等任何修改字符串的操作，都会创建新 String 变量或复用已有 String 变量，原 String 变量不会发生任何改变。
- 只能通过**反射**修改 `char[]/byte[]` 数组的内容，但是这个操作只会改变字节数组的内容，缓存的旧 hash 值不会改变，可能导致程序发生 bug。

### 2. 哈希值缓存

- 首次调用 hashCode() 时使用**滚动哈希**算法计算哈希值，并存储到 **hash** 字段，后续调用可以直接返回。因为 String 不可变，所以 **hash** 字段永远不会失效。

### 3. 字符串拼接

- 纯字面量、纯常量、字面量+常量的字符串拼接会被编译器直接优化为最终结果的字符串。
- 字符串变量拼接会被编译器优化为 `StringBuilder` 的 `append` 方法，如果字符串变量为 null，append 会处理为字符串 `"null"`。

### 4. JDK9 的压缩字符串

- jdk 9 将 String 的 value 从 char[] 改为 byte[] + coder，如果字符串为纯 Latin-1 字符，每个字符只是用一个 Byte 就可以存储；对于 UTF-16 的字符，仍使用 2B 存储。

# 四、泛型

- 泛型就是将类型参数化，从而提升代码的可读性和鲁棒性，将运行时类型检查提前到了编译时检查。
- 此外，泛型还可以自动进行强制类型转换，而不需要手动进行转换。

## (一) 泛型原理

- Java 通过**类型擦除**实现的泛型，在编译阶段对数据类型进行约束，编译器会将泛型替换为**顶级上界 Object** 或**指定上界**，在需要类型转换时会自动根据实际类型进行**强制类型转换**。

- <T> 会被替换为 Object，<T extends Number> 会被替换为 Number。

- 对 JVM 来说，只有不存在泛型的原始类和方法，所有的泛型实例都对应同一份擦除类型后的字节码。

## (二) 泛型通配符

- 核心原则 **PECS**：上界生产，下界消费。

### 1. 上界通配符 <? extend T>

- 表示集合中的对象可以是 T 及其子类。
- 用作参数时，方法会从该**集合中读取**数据。即只能从参数中读取，不能向参数中写入。

### 2. 下界通配符 <? super T>

- 表示集合中的对象可以是 T 及其父类。
- 用作参数时，方法会向该**集合中写入**数据。即只能向参数中写入，不能从参数中读取。

## (三) 泛型的限制/问题

- 泛型的限制主要来自于类型擦除机制，擦除后无法进行类型判断。

1. 只能声明不能实例化泛型变量。
2. 泛型只能是引用类型，不能是基本类型。

# 五、异常

## (一) 异常体系

1. Throwable

- 异常的根类。

1. Error：系统级异常，程序本身无法处理，也不应该尝试捕获。
2. Exception

- 编译时异常/检查性异常：编译时会进行检查，编译阶段必须处理。
- 运行时异常 **RuntimeException**：运行时检查，由代码错误导致，编译时不要求处理。`NullPointerException`、`ArithmeticException`、`IndexOutOfBoundsException`、`ClassCastException`、`IllegalArgumentException`等。

## (二) 异常处理

- 默认情况下，如果异常没有被捕获，会一直**向上传播**直到 main() 方法中。JVM 会将异常的类型、原因、位置等信息打印到控制台，然后程序从异常发生处终止执行，后续代码不再执行。

### 1. 抛出异常 throws/throw

- throws：在方法声明中，声明方法可能会出现的异常。当这些异常发生时，该异常会被传递给调用者，调用者必须处理或声明这些异常。
- throw：在方法内，用 throw 手动抛出异常，告诉调用方法代码执行状态，并且终止方法。

### 2. try-catch

```java
try{
    // 可能出现异常的代码块
}catch(异常类型 异常对象){ 
    // 捕获指定类型异常并处理异常的代码块
}finally{
    // 无论是否发生异常都要执行的代码块
}
```

- 如果 try 代码块中出现异常，就跳过 try 代码块中剩余代码，然后创建一个异常对象，并与 catch 语句进行比较。

- 如果该异常包含在 catch 语句指定的异常类型之中，就执行该 catch 块处理异常，执行完 catch 块后可以继续执行 try-catch 之后的代码。
- 如果没有 catch 语句可以捕获该异常，该异常会由 JVM 处理，继续向上传播。

- 如果可能出现多种异常，可以有多个 catch 块与之对应

- **子类异常应该放在父类异常上方**，否则子类异常的 catch 块永远不会被执行。
- 如果**多个异常**的处理方法相同，可以将他们写在一个 catch 语句中，异常之间**用 '|' 隔开**。

- 如果 try、catch、finally 中有多个 return，遇见 **return** 语句时会计算返回值并存入临时变量，按执行顺序后面的返回值会覆盖前面的返回值。

### 3. finally 代码块

- 从字节码层面看，finally 中的所有代码会被**复制到前面 try-catch 中的所有分支**，实现了所有可能分支都包含 finally 代码块。
- finally 中包含 return 语句，虽然允许这种语法，但是会带来以下问题

- 导致逻辑混乱，前面的 return 会被覆盖。
- 导致前面抛出的异常被抑制，无法向上抛出，调用者感知不到异常。

- finally 代码块一定会执行，除了下面的情况：

- 调用了 `System.exit()`。
- 线程被直接杀死。
- 系统奔溃/断电。
- 死循环。

### 4. try-with-resources

- JDK 7：可以在 try 语句中声明资源类变量，try 块执行完毕后会自动释放资源，后续代码都不能使用这些资源（包括 catch）。

```java
try(
    Resource1 resource1 = new Resource1("resource1");
    Resource2 resource2 = new Resource2("resource2");
   ){
    ...
}catch(异常类型 对象){ ... }
```

- JDK 9：资源可以在外部先声明，但是外部变量必须是 final 或等效于 final；在声明语句和 try 语句之间可以对资源进行检查，但是不能修改。

```java
Resource1 resource1 = new Resource1("resource1");
Resource2 resource2 = new Resource2("resource2");
try(resource1; resource2){
    ...
}catch(异常类型 对象){ ... }
```

# 六、Stream 流

- 结合 lambda 表达式，简化数组、集合的处理。

### 1. 创建 stream 流

- 集合类：.stream()
- 数组：Arrays.stream(T[] arr)
- 可变参数：Stream.of(T... elements)

### 2. 中间方法

- 中间方法返回的是一个新的流。

```java
Stream<T> filter(Predicate<? super T> predicate)	// 过滤 
Stream<T> limit(long maxSize) 						// 获取前几个元素 
Stream<T> skip(long n) 								// 跳过前几个元素 
static <T> Stream<T> concat(Stream a, Stream b) 	//合并a和b两个流为一个流 
Stream<T> distinct() 								// 元素去重（依赖hashCode()、equals()） 
Stream<R> map(Function<T,R> mapper)					// 转换流中数据类型 
Stream<T> sorted()									// 排序
```

### 3. 终结方法

```java
void forEach(Consumer<? super T> action)			// 对此流的每个元素执行操作 
long count()										// 返回此流中的元素数 
Object[] toArray()									// 收集流中的数据，放到数组中 
<R, A> R collect(Collector<? super T, A, R> collector)	// 收集流中的数据，放到集合中 
```

### 4. 工具类 Collectors

- 将 stream 转换为 list、set、map 或者不可变集合对象。
- 使用 toMap() 并自定义 key、value 的生成规则，将流转换为 Map。

# 七、注解

## (一) 元注解

- @Target：定义注解的作用域，例如：类和接口 ElementType.TYPE、字段 ElementType.FIELD、方法 ElementType.METHOD 等。
- @Retention：定义注解的生命周期。

- RetentionPolicy.SOURCE：只在编译期生效。
- RetentionPolicy.CLASS：默认，保留在 `.class`文件中，运行时不可见，一般给底层框架使用。
- RetentionPolicy.RUNTIME：保留在 `.class`文件中，可以在运行时通过反射访问，

- @Repeatable：定义注解是否可以在同一位置重复使用。
- @Inherited：定义子类是否可以继承父类注解。
- @Documented：javadoc 中是否包含该注解。

## (二) 原理与注解处理

- 注解是一种继承自 Annotation 的接口。真正使用注解时，JVM 会自动为这个。
- 处理注解需要使用反射 API 获取注解，然后使用得到的注解进一步实现对被修饰的类、方法等的增强或拦截。

# 八、深拷贝和浅拷贝

## (一) 浅拷贝

- 只复制对象本身以及内部的基本数据类型字段，即原对象持有的引用类型字段会直接复制到新对象中，新旧对象引用的是同一个引用对象。
- `Object.clone()` 默认是浅拷贝。

## (二) 深拷贝

- 基本数据类型直接复制。
- String 复用。
- 其他引用类型递归创建**新对象**并复制。

### 1. 手动递归复制

### 2. 实现 Cloneable 接口

- 要求对象及内部的所有引用类型字段都实现 Cloneable 接口并重写 **clone()** 方法。

### 3. 序列化与反序列化

- 将一个 Serializable  对象转换为字节流，再从字节流恢复为新对象。
- 当类结构发生变化时，自动生成的版本号也会变化。反序列化时，如果版本号不匹配，会抛出 `InvalidClassException`。

```java
public static <T extends Serializable> T deepCopy(T obj) throws IOException, ClassNotFoundException {
    // 序列化：将对象写入字节流
    ByteArrayOutputStream bos = new ByteArrayOutputStream();
    ObjectOutputStream oos = new ObjectOutputStream(bos);
    oos.writeObject(obj);
    oos.flush();
    oos.close();
     
    // 反序列化：从字节流恢复为新对象
    ByteArrayInputStream bis = new ByteArrayInputStream(bos.toByteArray());
    ObjectInputStream ois = new ObjectInputStream(bis);
    return (T) ois.readObject();
}
```

# 九、IO

## (一) BIO （Blocking I/O ，同步阻塞 IO）

- 应用程序发起 read 调用后，会一直阻塞，直到**内核**把数据拷贝到用户空间。

## (二) NIO（Non-blocking IO，同步非阻塞 IO）

- Java 1.4 引入了 java.nio，提供了 **Channel**、**Buffer**、**Selector** 等，实现 IO 多路复用。
- Java 的 nio 底层调用的系统调用，取决于系统的支持，一般都是 epoll 或者 kqueue 等算法。

### 1. Selector

- Selector 可以用一个线程监控多个通道上的事件，如：连接、读取、写入等。
- 所有的 Channel 都可以注册到 Selector 上，Selector 会**轮询** Channel 检查是否有事件发生。
- 当事件发生时，Channel 就处于就绪状态。没有时间的 Channel 不消耗资源。

```java
public static Selector open();										// 创建 Selector 对象。
public final SelectableChannel configureBlocking(boolean block);	// 将通道设置为非阻塞模式，才能注册到选择器。
public final SelectionKey register(Selector sel, int ops);			// 将通道注册到选择器，返回一个选择键。
public final int select();											// 轮询是否有以及有多少就绪的通道。
```

### 2. Buffer

- Buffer 是缓冲区的抽象类，最通用、常用的抽象类是 ByteBuffer。

```java
public static ByteBuffer allocate(int capacity);		// Buffer 子类的静态方法，在堆内存中分配一个缓冲区。
public static ByteBuffer allocateDirect(int capacity);	// Buffer 子类的静态方法，在直接内存中分配一个缓冲区。
public Buffer flip();		// 将缓冲区从"写模式"切换为"读模式"，调整 position、limit、mark。
public Buffer clear();		// 将 position、limit、mark 设置为初始状态，切换为"写模式"，旧数据仍然留在缓冲区。
public ByteBuffer compact();// 将 position ~ limit 之间的未读数据复制到缓冲区起始位置，切换为"写模式"，返回缓冲区的引用。
get()		// 读取缓冲区当前位置的数据
put()		// 向缓冲区当前位置写入数据
```

- Buffer 的核心参数

```
// Invariants: mark <= position <= limit <= capacity private int mark = -1; private int position = 0; private int limit; private int capacity;
```

- **mark**：用来记录某次的 position，通过 **mark**() 将 mark 设置为当前的 position。
- **postion**：表示下一次读取或写入数据的索引，使用 **reset**() 可以将 position 恢复为上次设置的有效的 mark。
- **limit**：表示当前最大能够写入或读取的数据的索引，超出 limit 限制的数据不允许读写。
- **capacity**：表示缓冲区的容量，缓冲区创建后不允许修改。

### 3. Channel

- Channel 是通道的抽象接口，面向块。
- 读写必须经过 Buffer，一端是 Buffer，另一端一般是文件或者套接字。
- Channel 是双向的，同一个 Channel 既能读也能写。
- read() 从另一端读取数据并写入 Buffer；write() 从 Buffer 读取数据写入另一端。

```java
public final xxxChannel getChannel();								// 通过支持通道的类对象调用 getChannel() 创建通道
public static SeekableByteChannel newByteChannel(Path path, OpenOption... options);		// Files 的静态方法创建 ByteChannel
public static FileChannel open(Path path, OpenOption... options)	// 通过通道实现类的 open() 方法创建通道
public static DatagramChannel open()
```

### 4. 零拷贝

|                            | CPU 拷贝 | DMA 拷贝 | 系统调用   | 模式切换 |
| -------------------------- | -------- | -------- | ---------- | -------- |
| 传统 IO                    | 2        | 2        | read+write | 4        |
| mmap+write                 | 1        | 2        | mmap+write | 4        |
| sendfile                   | 1        | 2        | sendfile   | 2        |
| sendfile + DMA gather copy | 0        | 2        | sendfile   | 2        |

- **MappedByteBuffer** 是 NIO 基于内存映射（**mmap**）这种零拷贝方式的提供的⼀种实现，底层实际是调用了 Linux 内核的 mmap 系统调用。它可以将一个文件或者文件的一部分映射到内存中，形成一个虚拟内存文件，这样就可以直接操作内存中的数据，而不需要通过系统调用来读写文件。
- **FileChannel** 的 **transferTo**()/**transferFrom**() 是 NIO 基于发送文件（sendfile）这种零拷贝方式的提供的一种实现，底层实际是调用了 Linux 内核的 `**sendfile**` 系统调用。它可以直接将文件数据从磁盘发送到网络，而不需要经过用户空间的缓冲区。

## (三) AIO（Asynchronous I/O，异步 IO)

- 异步 IO 是基于**事件**和**回调机制**实现的，应用程序只负责发起请求和处理结果，而不会阻塞在调用 AIO 地方，IO 由操作系统完成。当 IO 完成后，操作系统会通知线程处理数据。
- 当操作系统将数据**读入内存后**，通过**回调**通知应用程序处理数据。

## (四) 序列化流

- 序列化就是将一个 **Serializable**  对象转换为字节流的过程，反序列化就是将字节流重新转换为对象。
- 对象序列化的必要条件：

- 该类必须实现 **Serializable** 接口，否则会抛出 `NotSerializableException`异常。
- 所有属性都必须是可序列化的，如果有不需要序列化的属性，该属性必须用 **transient** 关键字修饰。

- 类对象序列化后写到文件中的数据不能修改，否则无法成功反序列化。
- 需要序列化的类应该显式定义 **serialVersionUID** 属性，否则 JVM 会自动生成一个版本号。如果类结构发生变化，版本号就会发生变化。反序列化时，如果版本号不匹配，会抛出 `InvalidClassException`。

# 十、equals() 与 hashCode()

## (一) 规约

- 同一对象多次调用 hashCode() 应该返回相同值。
- equals() 返回 true 时， hashCode() 应该返回相同值。
- equals() 返回 false 时， hashCode() 可以返回相同值。

## (二) 重写

- 未重写的 hashCode()、equals() 默认按照对象的**地址值**计算，不同对象 hashCode() 一定不同、equals() 一定返回 false。
- 重写后一般根据对象的属性值计算

- hashCode() 不同对象属性值相同一定相同，属性值不同可能相等即哈希碰撞。
- equals() 不同对象属性值相同一定 true，属性值不同一定 false。

- 为了防止 HashMap 等 hash 容器中出现**重复元素**，hashCode()、equals() **必须一起重写**，实现容器中**两个逻辑相等的对象必须返回相同哈希值**。即 equals() 返回 true 时， hashCode() 应该相同。



# 十一、BigDecimal

- BigDecimal 用来进行高精度大数计算。
- 将整数部分和小数部分分别存储，不会丢失精度。
- 推荐使用字符串初始化，因为使用浮点数字面量初始化，这个浮点数本身会丢失精度。



# 十二、API 与 SPI

|              | API                               | SPI                                     |
| ------------ | --------------------------------- | --------------------------------------- |
| **全称**     | Application Programming Interface | Service Provider Interface              |
| **定位**     | 面向开发者提供的**接口**          | 面向扩展者提供的**扩展点**              |
| **调用方向** | **开发者调用框架的接口**          | **框架调用开发者的扩展**                |
| **控制权**   | 框架定义，开发者调用              | 框架定义接口，开发者实现                |
| **核心目的** | 提供功能接口                      | 提供扩展能力                            |
| **典型示例** | `List.add()`、`Thread.start()`    | JDBC Driver、SLF4J、Spring Boot Starter |
| **发现方式** | 直接调用                          | 配置文件 + `ServiceLoader` 动态加载     |

# 十三、Unsafe

- Unsafe 类提供了直接操作内存、线程和硬件等的底层方法，通过本地方法和操作系统、内存直接交互。
- Unsafe 类只能通过`getUnsafe()`方法获取的实例（单例），但是只有`BootstrapClassLoader`或`PlatformClassLoader`（JDK 9 以后允许）加载的类可以使用该方法获得 Unsafe 的实例。

- 通过反射调用`getUnsafe()`获得 Unsafe 中的实例。
- 通过`-Xbootclasspath/a:路径`（JDK 8）或`--patch-module`（JDK 9 之后）等参数将自定义包追加到`BootstrapClassLoader`可以加载的路径。

## (一) 内存操作

- 通过这些方式申请的内存都是直接内存，不受 JVM 的 GC 管理，例如：`DirectByteBuffer`的实现就是用 Unsafe 的内存操作的相关方法。

```java
// 分配 bytes 字节的内存空间
public long allocateMemory(long bytes);
// 从 offset 将连续 bytes 字节内存设置为 value
public void setMemory(Object o, long offset, long bytes, byte value);
// 从原地址复制 bytes 字节的内存到目的地址
public void copyMemory(Object srcBase, long srcOffset, Object destBase, long destOffset, long bytes);
// 释放 address 处申请的内存空间
public void freeMemory(long address);
```

## (二) 对象操作

- 提供了 8 种基本数据类型（byte、short、 int、long、float、double、char、boolean）的 get、put 方法。对 Object 提供了`getReference/getObject`、`putReference/putObject`方法。
- 对 8 个基本数据类型和 Object 还提供了`getxxxVolatile`指令，可以保证变量读写的可见性和有序性，读写变量时强制写入或者读取内存中的最新值。
- 有序写入可以保证写入时的有序性，但是不能保证可见性。

```java
public native int getInt(Object o, long offset);
public native void putInt(Object o, long offset, int x);
public native int getIntVolatile(Object o, long offset);
public native void putIntVolatile(Object o, long offset, int x);
public native void putOrderedObject(Object o, long offset, Object x);
```

- 通过allocateInstance 创建的对象不会调用构造函数。

```java
public native Object allocateInstance(Class<?> cls);
```

## (三) 数组操作

- `arrayBaseOffset``arrayIndexScale`两个方法可以获得数组首地址和元素大小，在`AtomicIntegerArray`中使用这两个方法。

```java
public int arrayBaseOffset(Class<?> arrayClass);	// 返回数组第一个元素的首地址
public int arrayIndexScale(Class<?> arrayClass);	// 返回数组中一个元素占据内存空间的大小
```

## (四) CAS

- CAS 操作底层使用的是 CPU 的一条原子指令，当内存中的值与预期值相同时，则进行更新并返回 true，否则返回 false。

```java
public final native boolean compareAndSetInt(
    Object o, 		// 需要修改的对象
    long offset,	// 字段在对象中的偏移量
    int expected,	// 预期值
    int x			// 更新值
);
```

## (五) 线程调度

- `AbstractQueuedSynchronizer`框架获取和释放锁是通过`LockSupport`的 park、unpark 方法实现的，这两个方法的实现就是直接调用 `Unsafe`的 park、unpark。

```java
public native void park(boolean isAbsolute, long time);	// 阻塞线程
public native void unpark(Object thread);				// 唤醒被 park 阻塞的线程
```

# 十四、**CompletableFuture**

- CompletableFuture 采用了一种链式的结构来处理异步计算的结果，每个CompletableFuture 都有一个与之关联的Completion链，它可以包含多个Completion阶段，每个阶段都代表一个异步操作，并且可以指定它所依赖的前一个阶段的计算结果。(在CompletableFuture类中，定义了一个内部类Completion，它表示Completion链的一个阶段，其中包含了前一个阶段的计算结果、下一个阶段的计算操作以及执行计算操作的线程池等信息。)
- CompletableFuture 的异步计算是通过线程池来实现的。CompletableFuture在内部使用了一个ForkJoinPool线程池来执行异步任务。当我们创建一个CompletableFuture对象时，它会在内部创建一个任务，并提交到ForkJoinPool中去执行。

# 十五、语法糖

## (一) switch

- 对于 JVM 来说，switch 只能使用整形，char、byte 等基本数据类型都可以转换为整型。
- String：switch 对 String 的支持是通过 `hashCode()`和`equals()`方法实现的，
- enum：switch 对 enum 的支持时通过`ordinal()`方法计算枚举常量在枚举类中的顺序索引实现的。

## (二) 可变长参数

- 允许实参传递 0 个或多个数据，或者是一个数组。基本类型的数组会当作一个引用变量看，引用类型数组则是当作一个引用数组看。
- 一个方法只能有一个可变参数，且只能放参数列表

```java
void print(String... strs);
```

# 十六、新特性

| **JDK8**  | Lambda 表达式、Stream、接口默认方法+静态方法、方法引用。     |
| --------- | ------------------------------------------------------------ |
| **JDK11** | HTTP Client 正式版、ZGC 回收器。String 优化了底层存储 (byte 数组+compact 存储)、新增一些方法。 |
| **JDK17** | Record 不可变类、instanceof 支持模式匹配。                   |
| **JDK21** | 虚拟线程、Switch 支持模式匹配。                              |

### 1. Record

- JDK 16 正式引入，设计用于充当不可变数据的透明载体，主要目的是减少样板代码，可以自动生成：字段、构造器、访问方法、equals、hashCode、toString 等。
- record 修饰的类隐式继承自 **Record** 类，具有以下特点：

- final 类、final 字段；
- 可以有静态方法、静态字段、成员方法，但是除了记录头中的成员变量不能单独声明成员字段；
- 可以实现接口，但是不能继承类，因为隐式继承了 Record 类；
- 可以自定义非全参构造器，但是必须通过 **this()** 调用全参构造器；
- 可以自定义全参构造器，但是必须为所有字段赋值。
