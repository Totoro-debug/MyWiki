# 一、Spring 框架

## (一) IOC

### 1. **控制反转（Inversion of Control，IOC）**

- IOC 指开发者不通过 new 手动创建对象或维护依赖关系，而是由框架负责创建对象、依赖管理。

### 2. 依赖注入（Dependency Injection，DI）

- DI 是实现 IOC 的一种方式。开发者只需要用配置文件或注解声明对象的依赖关系，Spring 容器会自动创建对象并注入当前对象依赖的对象。

- 构造器注入。
- Setter() 注入。
- 注解注入（字段、类上加注解）。

### 3. Spring 容器（Container）

- 容器是 IOC 的载体，负责对象的创建、依赖注入、生命周期管理等操作。
- `BeanFactory`最基础的容器，提供基本的 IOC 功能，采用懒加载。
- `ApplicationContext`扩展了更多功能，采用预加载单例对象。

## (二) Bean

- Bean 指由 Spring 容器管理的对象，Bean 的生命周期由 Spring 容器管理。

### 1. 创建 Bean 的方式

- XML 配置中使用 <bean> 标签定义 Bean。
- 使用 `@Bean` 声明 Bean，一般在 `@Configuration` 配置类中使用 `@Bean` 注解表示方法返回的是一个 Bean。
- 在配置类上使用 `@Import` 导入多个类并生成 Bean。
- `@Component`通用的注解、`@Service`、`@Repository`、`@Controller`用于接受用户请求并调用 Service 层。

### 2. @Autowired 和 @Resource 的区别

- `@Autowired` 是 Spring 内置的注解。默认注入逻辑为先按类型（byType）匹配，若存在多个同类型 Bean，则再尝试按名称（byName）筛选。
- `@Resource` 是 JDK 提供的注解。默认按照名称查找，找不到再根据类型查找，如果只有一个 Bean 返回成功，否则抛出异常。

### 3. Bean 的生命周期

1. **创建 doCreateBean()**

2. 实例化 **createBeanInstance()**

- 根据 **BeanDefinition** 决定使用构造器或者工厂方法等创建并返回 Bean 实例。

2. 属性注入 **populateBean()**

- 注入 `@Autowired`、`@Value` 等注释标注的字段或 Setter、配置文件中的依赖。

3. 初始化 **initializeBean()**

- **invokeAwareMethods()** 检查是否实现了 `Aware` 接口 (3 个)，如果有则调用相应方法。
- **applyBeanPostProcessorsBeforeInitialization()** 检查是否实现了 `BeanPostProcessor`接口并调用 **postProcessBeforeInitialization()**，此过程中会调用 **@PostConstruct** 修饰的方法。

- 其中`InitDestroyAnnotationBeanPostProcessor`类专门处理自定义注解标记的初始化方法和销毁方法，典型方法就是 **@PostConstruct**、**@PreDestroy**。

- **invokeInitMethods()** 首先检查是否实现了`InitializingBean` 接口，是则调用 **afterPropertiesSet()**；然后调用 **init-method** 方法。
- **applyBeanPostProcessorsAfterInitialization()** 检查是否实现了 `BeanPostProcessor`接口并调用 **postProcessAfterInitialization()**。

4. 注册销毁回调方法 **registerDisposableBeanIfNecessary()**

- 如果实现了 `DisposableBean`接口或者自定义了 destory-method 方法，为 Bean 注册销毁回调方法。

2. 就绪
3. 销毁：容器关闭时，调用`DisposableBean`接口的 destory() 方法和 destory-method 方法。

### 4. 三级缓存

- 三级缓存不能解决构造器注入的循环依赖，可以解决 Setter、字段注入。

1. **一级缓存 singletonObjects** 存放已经初始化完的完整单例 Bean。

- 此时 Bean 已经完成实例化、属性注入、初始化。如果需要 AOP 代理，则存放代理对象。

2. **二级缓存 earlySingletonObjects** 存放未完全创建的 Bean 或早期代理对象。

- 创建单例 Bean 时，发现存在循环依赖，会调用三级缓存中的对象工厂实例化 Bean 或生成早期代理对象并放到二级缓存中，同时删除三级缓存中的对象工厂。

3. **三级缓存 singletonFactories** 存放 Bean 的对象工厂 ObjectFactory。

- Bean 被实例化后，Spring 会创建它的对象工厂并放到三级缓存中。`ObjectFactory.getObject()`返回原始对象或者早期代理对象。

4. 缓存依赖处理过程

- 首先调用`doGetBean()`尝试从缓存中获取 A，因为 A 还没有创建`getSingleton(String)`返回 null，然后调用`getSingleton(String, ObjectFactory<?>)`触发`createBean() -> doCreateBean()`。
- A 实例化完成后，创建 A 的对象工厂并放入三级缓存中。A 依赖注入时发现依赖 B，调用 `autowireByName() -> getBean() -> doGetBean() -> getSingleton(String)`。因为 B 没有创建 `getSingleton(String)` 返回 null，然后调用`getSingleton(String, ObjectFactory<?>)`触发`createBean() -> doCreateBean()`。
- B 实例化完成后，创建 B 的对象工厂并放入三级缓存中。B 依赖注入时发现依赖 A，此时 **getSingleton()** 查询三级缓存时能查到 A 的对象工厂，调用 getObject() 创建 A 原始对象或者早期代理对象并插入到二级缓存，同时删除 A 的三级缓存。
- B 完成依赖注入、初始化后，退出 A 的 getSingleton() 中调用的 createBean()，然后调用 `addSingleton()`将 B 的 Bean 加入一级缓存，并清空 B 的二级缓存和三级缓存。然后退出 A 的 getSingleton()，最后完成 A 的依赖注入、初始化。
- A 初始化完成后，调用 addSingleton() 将 A 的 Bean 加入一级缓存，并清空 A 的二级缓存和三级缓存。

## (三) AOP

- **面向切面编程（Aspect-Oriented Programming，AOP）**旨在将与业务无关的日志、事务等公共逻辑封装成模块，减少代码重复性和耦合性，提高可扩展性和可维护性。
- 基于**动态代理**实现，当目标类实现了至少一个接口时，默认用 JDK 动态代理，否则用 **CGLIB** 实现。
- 在 Bean 实例化完成后进行初始化的后置处理时创建代理对象。

### 1. AOP 增强的场景

- 类或类中的方法被切点 `@Aspect` 匹配，如自定义日志、缓存等切面类。
- 类或方法使用 @Transactional 时。
- 类实现了 ApplicationContextAware、InitializingBean 等接口时。

## (四) Spring 事务

1. 编程式事务：基于 TranasctionTemplate、PlatformTransactionManager 等接口，在代码中手动实现事务的开启、提交、回滚等。
2. 声明式事务：为类/方法添加 **@Tranasctional** 注解或使用 XML 配置事务。通过 AOP 动态代理为目标方法增加事务逻辑，事务粒度最小只能是方法。

### 1. 事务传播行为

- 控制多个**事务方法嵌套**调用时的事务行为，避免事务不⼀致、数据丢失、重复提交等问题，保证一致性、完整性。

1. `**REQUIRED**`：默认行为，创建或加入（需要事务）。A 调用 B，如果 A 存在事务，则将 B 加入 A 的事务；否则，B 创建新的事务。
2. `**REQUIRES_NEW**`：**总是新建事务**。A 调用 B，A 事务暂停，B 新建事务。且 A、B 的事务提交/回滚**互不影响**。
3. `**SUPPORTS**`：支持事务，随便有没有。如果 A 存在事务则加入；否则，无事务直接执行。
4. `**NOT_SUPPORTED**`：不允许事务。如果当前存在事务，则**暂停当前事务**。
5. `**MANDATORY**`：强制在事务中运行。有事务则加入，无事务抛异常。
6. `**NEVER**`：强制以非事务运行。无事务则执行，有事务抛异常。
7. `**NESTED**`：嵌套事务，基于 **Savepoint** 实现。如果 A 存在事务，B 创建子事务，子事务回滚不会导致父事务回滚，父事务回滚会导致子事务回滚。

### 2. 事务失效

1. **数据库引擎不支持事务**：Mysql 的 InnoDB 支持事务，但是 MyISAM 等不支持事务。
2. **Bean 没有被 Spring 管理**：调用该方法的 Bean 没有被 Spring 管理，方法调用没有走代理对象，Spring AOP 失效。
3. **同一个类自调用**：A 直接调用同一个类的方法 B，绕过了 AOP，B 的事务失效，B 被加入到 A 的事务中。
4. **方法非 public**：@Transactional 等依赖于 SpringAOP 实现的注解都只能在 public 方法上起作用。
5. **异常被手动 catch 且没有抛出**：异常在方法内部被 catch 后没有再次抛出，AOP 无法感知异常，无法回滚。
6. **异常类型超出处理范围**：Spring 默认只对 **RuntimeException** 及其子类异常回滚。如果需要检测的异常超出 RuntimeException，应该手动设置 **rollbackFor** 属性。
7. **多线程调用**：Spring 事务上下文存储在 ThreadLocal 中。多线程中，父子线程的事务相互独立，无法保证两者的一致性。
8. **事务传播属性**：事务传播属性 propagation 设置不合理。

## (五) Spring 设计模式

- 工厂模式：IOC
- 单例模式：Bean 默认单例。
- 代理模式：使用 AOP 增强被代理的类。
- 模板方法模式：Template 类。

# 二、SpringBoot

- 自动配置：使用约定大于配置思想，使得许多配置可以自动完成。默认读取 spring.factories 加载 Starter，读取 application.prperties/yml 进行属性配置。
- 快速启动：SpringBoot 内嵌了 tomcat、jetty 等服务器，可以快速启动程序。
- 依赖引入：引入一个 Starter 就可以将常用框架引入，提高开发效率。

## (一) 自动装配

- `**@SpringBootApplication**`注解中`**@EnableAutoConfiguration**`注解是实现自动装配的核心注解。EnableAutoConfiguration 使用`**@Import**`导入 `**AutoConfigurationImportSelector**`的 Bean，最后调用 `ImportCandidates.load` 读取 **imports** 文件中的所有自动配置类的全类名，根据各种条件注解（`@ConditionalOnMissingBean`等）过滤不满足条件的配置类，最后将所有 Bean 注册到容器中。

## (二) SpringBoot 启动流程

# 三、SpringMVC

- Model-View-Controller 将软件分为模型、视图、控制器。视图为用户提供界面，模型负责数据承载和业务处理，控制器将用户请求转发给模型，使试图和模型分离。

![](https://cdn.nlark.com/yuque/0/2026/png/46298582/1775582117679-603a1234-2760-485d-a084-c20d36ce3f92.png)