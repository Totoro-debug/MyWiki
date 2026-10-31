# Spring

原文：[02-Java 后端/Spring.md](../../../02-Java%20%E5%90%8E%E7%AB%AF/Spring.md)
SHA-256：`19e910c663fef3412e18e719302350417e566c457a637fe22ab9ea44b4e13b82`

本卡为自动导航与逐字摘录；回答前使用 `wiki.py read` 核对原文。

- L1-L2 · 一、Spring 框架
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

- L23-L26 · 一、Spring 框架 > (二) Bean

  摘录（原文）：

  ```text
  - Bean 指由 Spring 容器管理的对象，Bean 的生命周期由 Spring 容器管理。
  ```

- L27-L33 · 一、Spring 框架 > (二) Bean > 1. 创建 Bean 的方式

  摘录（原文）：

  ```text
  - XML 配置中使用 <bean> 标签定义 Bean。
  ```

- L34-L38 · 一、Spring 框架 > (二) Bean > 2. @Autowired 和 @Resource 的区别

  摘录（原文）：

  ```text
  - `@Autowired` 是 Spring 内置的注解。默认注入逻辑为先按类型（byType）匹配，若存在多个同类型 Bean，则再尝试按名称（byName）筛选。
  ```

- L39-L67 · 一、Spring 框架 > (二) Bean > 3. Bean 的生命周期

  摘录（原文）：

  ```text
  1. **创建 doCreateBean()**
  ```

- L68-L91 · 一、Spring 框架 > (二) Bean > 4. 三级缓存

  摘录（原文）：

  ```text
  - 三级缓存不能解决构造器注入的循环依赖，可以解决 Setter、字段注入。
  ```

- L92-L97 · 一、Spring 框架 > (三) AOP

  摘录（原文）：

  ```text
  - **面向切面编程（Aspect-Oriented Programming，AOP）**旨在将与业务无关的日志、事务等公共逻辑封装成模块，减少代码重复性和耦合性，提高可扩展性和可维护性。
  ```

- L98-L103 · 一、Spring 框架 > (三) AOP > 1. AOP 增强的场景

  摘录（原文）：

  ```text
  - 类或类中的方法被切点 `@Aspect` 匹配，如自定义日志、缓存等切面类。
  ```

- L104-L108 · 一、Spring 框架 > (四) Spring 事务

  摘录（原文）：

  ```text
  1. 编程式事务：基于 TranasctionTemplate、PlatformTransactionManager 等接口，在代码中手动实现事务的开启、提交、回滚等。
  ```

- L109-L120 · 一、Spring 框架 > (四) Spring 事务 > 1. 事务传播行为

  摘录（原文）：

  ```text
  - 控制多个**事务方法嵌套**调用时的事务行为，避免事务不⼀致、数据丢失、重复提交等问题，保证一致性、完整性。
  ```

- L121-L131 · 一、Spring 框架 > (四) Spring 事务 > 2. 事务失效

  摘录（原文）：

  ```text
  1. **数据库引擎不支持事务**：Mysql 的 InnoDB 支持事务，但是 MyISAM 等不支持事务。
  ```

- L132-L138 · 一、Spring 框架 > (五) Spring 设计模式

  摘录（原文）：

  ```text
  - 工厂模式：IOC
  ```

- L139-L144 · 二、SpringBoot

  摘录（原文）：

  ```text
  - 自动配置：使用约定大于配置思想，使得许多配置可以自动完成。默认读取 spring.factories 加载 Starter，读取 application.prperties/yml 进行属性配置。
  ```

- L145-L148 · 二、SpringBoot > (一) 自动装配

  摘录（原文）：

  ```text
  - `**@SpringBootApplication**`注解中`**@EnableAutoConfiguration**`注解是实现自动装配的核心注解。EnableAutoConfiguration 使用`**@Import**`导入 `**AutoConfigurationImportSelector**`的 Bean，最后调用 `ImportCand …〔截断〕
  ```

- L149-L150 · 二、SpringBoot > (二) SpringBoot 启动流程 〔未填写〕
- L151-L155 · 三、SpringMVC

  摘录（原文）：

  ```text
  - Model-View-Controller 将软件分为模型、视图、控制器。视图为用户提供界面，模型负责数据承载和业务处理，控制器将用户请求转发给模型，使试图和模型分离。
  ```


## 读取入口

```powershell
python LLMWiki/wiki.py read "02-Java 后端/Spring.md" --start 1 --end 80
```
