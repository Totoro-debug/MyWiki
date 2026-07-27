# 一、线程

## (一) 进程和线程的区别

- 进程是操作系统资源分配的基本单位，而线程是处理器任务调度和执行的基本单位。
- 每个进程都有独立的地址空间和资源，进程切换开销较大；同一进程的线程共享进程的地址空间和资源，每个线程都有自己独立的运行栈和程序计数器，线程切换开销较小。
- 一个进程崩溃后，在保护模式下不会对其他进程产生影响，但是一个线程崩溃有可能导致整个进程都死掉。所以多进程要比多线程健壮。

## (二) 操作系统线程实现方式

1. 内核级线程（Kernel-Level Thread,KLT）

- 线程由操作系统内核创建、调度。
- 应用程序一般不会直接使用内核级线程，而是通过高级接口轻量级进程（Light Weight Process, LWP）使用。

2. 用户级线程

- 通过运行时系统进行线程的管理，可以运行在任何操作系统。

## (三) Java 线程与系统线程的关系

- JDK1.2 之后，Java 线程和内核线程之间采用 **1:1 映射**模型，Java 线程的控制与调度全都依赖于 JVM 调用操作系统提供的 API。

## (四) 创建线程

### 1. 继承 Thread 类

- 自定义类继承 Thread 类，重写 run() 方法。
- 创建类对象，用 start() 方法启动线程。

```
public class MyThread extends Thread {
    @Override
    public void run() {
        // ...
    }
}

MyThread t = new MyThread();
t.start();
```

### 2. 实现 Runable 接口

- 自定义类实现 Runable 接口，重写 run() 方法。
- 用实现类对象作为参数创建 Thread 对象，用 start() 方法启动线程。

```
public class MyRunnable implements Runnable {
    @Override
    public void run() {
        // ...
    }
}

Thread t = new Thread(new MyRunnable());
t.start();
```

### 3. 实现 Callable 接口（Future 模式）

- 自定义类实现 Callable 接口，重写 call() 方法。
- 用实现类对象作为参数创建 FutureTask 对象。
- 将 FutureTask 对象作为参数创建 Thread 对象，用 start() 方法启动线程。
- 自定义类对象调用 get() 方法可以拿到 call() 方法的结果。

```
public class MyCallable implements Callable<String> {
    @Override
    public Object call() throws Exception {
        // ...
    }
}

MyCallable mc = new MyCallable();
FutureTask<Object> ft = new FutureTask<>(mc);
Thread t1 = new Thread(ft);
t1.start();
String s = ft.get();
```

## (五) 停止线程

1. 共享标志位

- 使用 volatile 变量或者锁保证变量可见性。

2. 中断机制

- 使用`interrupt()`方法中断线程，线程内通过检测中断标志主动停止。

3. 线程池与 Future

- 使用线程池提交任务会返回一个 Future 对象，可以通过`cancel()`方法停止线程。

4. stop()

- 不推荐暴力停止线程，直接 stop 线程可能导致一些清理性的工作无法完成，造成状态不一致的问题。

## (六) 虚拟线程

- JDK 21 正式引入的新特性。一个 Java 线程可以对应很多个虚拟线程，虚拟线程作为普通的 Java 对象存储在内存中，所以虚拟线程的切换不存在上下文开销。
- 虚拟线程与平台线程区别

- 虚拟线程总是守护线程，`setDaemon()`方法对虚拟线程无效。
- 虚拟线程的优先级固定为 normal，`setPriority()`方法对虚拟线程无效。
- 虚拟线程不支持 stop()、suspend() 等方法。

- 虚拟线程不适合用线程池池化，因为虚拟线程非常轻量，使用线程池反而增加了上下文切换的开销。
- 不要在同步代码块/同步方法中使用虚拟线程、虚拟线程中不要使用本地方法，否则可能无法实现虚拟线程的自动挂起和调度。

1. **直接创建并运行**

```
// 传入Runnable实例并立刻运行:
Thread vt = Thread.startVirtualThread(() -> { ... });
```

2. **ofVirtual() 创建并用 start() 运行**

- 通过 ofVirtual() 与 start() 的方式本质上是通过 ForkJoinPool 调度。

```
// ofVirtual() 方式1
Thread.ofVirtual().unstarted(() -> { ... });
vt.start();
// ofVirtual() 方式2
Thread.ofVirtual().start(() -> { ... });
```

3. **虚拟线程工厂创建**

```
// 创建ThreadFactory:
ThreadFactory tf = Thread.ofVirtual().factory();
// 创建VirtualThread:
Thread vt = tf.newThread(() -> { ... });
// 运行:
vt.start();
```

4. **虚拟线程池创建**

- 本质上还是使用 **Thread.ofVirtual().factory()** 创建虚拟线程。

```
// 创建调度器:
ExecutorService executor = Executors.newVirtualThreadPerTaskExecutor();
// 提交任务
executor.submit(() -> {
    System.out.println("Start virtual thread...");
    Thread.sleep(1000);
    System.out.println("End virtual thread.");
    return true;
});
```

## (七) Java 线程的生命周期

<img src="00-resource/images/Java线程生命周期.png" style="zoom:75%;">

|   |   |
|---|---|
|线程状态|含义|
|NEW|线程已创建，还未调用 start() 方法启动。|
|RUNNABLE|线程对象调用了 start() 方法，线程进入就绪队列，竞争处理器，等待系统调度；或者线程正在运行。|
|BOLCKED|当线程获取 synchronized 锁失败或 wait() 后被 notify() 竞争锁失败，则进入阻塞状态。当锁重新可用后，线程会自动恢复为 RUNNABLE。|
|WAITING|线程因为 wait()、join()、park() 等方法，无限制地等待其他线程执行特定事件唤醒自己。如：使用 wait() 的线程等待其他线程 notify() 或 notifyAll()，使用 join() 的线程等待目标线程运行结束而唤醒，使用 park() 的线程等待其他线程 unpark(Thread)。|
|TIMED_WAITING|线程因为 sleep(long)、wait(long)、join(long)、parkNanos(long) 等方法，等待有限时间后或被特定事件唤醒后，重新进入 RUNNABLE 状态。|
|TERMINATED|线程执行完毕或者因为其它原因终止。|

## (八) Thread 常用方法

|   |   |
|---|---|
|方法|说明|
|**Thread(Runnable)**|如果创建线程时传入了 Runnable 对象，在执行 run() 方法时就会执行Runnable 对象的 run() 方法，否则不执行操作。|
|**start()**|使线程进入`RUNNABLE`状态，JVM 调用操作系统 API 创建内核线程。start() 会检查threadStatus==0，所以每个线程只能调用一次该方法，多次调用会抛出`IllegalThreadStateException`异常。|
|**run()**|线程进入运行状态后，JVM 会调用该线程的 run() 方法。如果直接手动调用 run() 方法，会被当做普通方法执行，对应的线程也不会启动。|
|**yield()**|使当前线程进入`RUNNABLE`状态，只能保证当前线程放弃 CPU，不能保证其它线程一定能占用 CPU，当前线程也可能立即抢占到 CPU。|
|**sleep()**|使当前线程进入`TIMED_WAITING`状态，等待指定时间后进入`RUNNABLE`状态，过程中被中断会抛出`InterruptedException`异常。|
|**join()**|使当前线程进入`TIMED_WAITING / WAITING`状态，当前线程会在调用线程的监视器上等待，直到调用线程执行结束，或经过指定时间，或被中断并抛出`InterruptedException`异常。|
|**interrupt()**|如果线程正在运行，设置中断标志；如果线程被 sleep、join、wait、await 等阻塞会抛出 InterruptedException，并清除中断标志；如果线程被 park 阻塞，只设置中断标志。|
|**isInterrupted()**|返回中断标志。|
|**interrupted()**|返回中断标志，并清除中断标志。|
|**setDaemon()**|将调用线程设置为守护线程。守护线程在后台运行，为用户线程提供服务；当用户线程全部执行完后，守护线程会随 JVM 一起结束运行。|

# 二、线程安全

## (一) 临界区与竞态条件

- **临界区**：同一时刻只有一个线程可以访问的代码块称为临界区，通常用于控制对共享资源的多线程互斥访问。
- **竞态条件**：多个线程并发执行时，指令的执行顺序不同会导致最终结果不同。

## (二) 变量的线程安全

### 1. 成员变量、静态变量

- 非共享变量，则线程安全。
- 共享变量，如果只有读操作，则线程安全；如果有写操作，则需要考虑线程安全。

### 2. 局部变量

- 局部变量本身是线程安全的。
- 局部变量如果是引用变量，如果引用对象不会暴露在方法外，就是线程安全的；否则需要考虑线程安全。

### 3. 常见线程安全类

- 不可变类：String、包装类Integer、BigDecimal、BigInteger等。

- final 的使用

- 属性用 final 修饰保证了该属性是只读的，不能修改。
- 类用 final 修饰保证了该类不能被继承，方法不会被覆盖。

- 保护性拷贝

- 当需要修改对象时，通过创建副本对象避免共享。

- 原子的方法：StringBuffer、Random、Vector、Hashtable。
- JUC 中的并发安全类。

## (三) 死锁、活锁、饥饿

### 1. 死锁

- 死锁就是两个或多个线程相互持有对方需要的资源，导致这些线程都处于等待状态，若无外力作用，都无法向前推进。
- 必要条件

- **互斥**：资源不能被多个线程同时使用。
- **请求和保持**：线程已经持有至少一个资源，同时请求其他资源。
- **不剥夺**：线程持有的资源在使用完前不能被强行剥夺。
- **环路等待**：存在一个循环等待链，每个线程都在等待下一个线程持有的至少一个资源。

- 避免死锁

- 避免一个线程同时获得多个锁。
- 避免一个线程在锁内同时占用多个资源，尽量保证每个锁只占用一个资源。
- 使用 tryLock() 代替 synchronized/lock()。

- 死锁检测

- 使用 jmap、jstack 等命令查看 JVM 线程栈和堆内存的情况。如果有死锁，jstack 的输出中通常会有 Found one Java-level deadlock:的字样，后面会跟着死锁相关的线程信息。

### 2. 活锁

- 两个线程相互改变对方的结束条件，导致都无法结束。
- 两个线程互相持有对方需要的资源，然后都释放资源，重复不断的申请-释放，导致都不能执行。

### 3. 饥饿

- 一个线程因为优先级太低，或者是因为需要的资源始终被其他线程占据，导致始终无法得到执行。

# 三、Java 内存模型（JMM）

- JMM 屏蔽了不同硬件和操作系统的内存访问差异，规定了多线程程序中共享变量的访问方式以及线程间通信的底层细节。
- **确保可见性**：线程对共享变量的修改能及时被其他线程看到。
- **确保原子性**：对变量的读写操作不可分割。
- **确保有序性**：通过 happens-before 规则禁止特定指令重排序，避免并发问题。
- JMM 中将内存分为主内存、工作内存。

- **主内存**中存放线程中创建的所有实例对象，包括成员变量、局部变量、类信息、常量等。
- **工作内存**中存放线程需要读写的共享变量的副本。

## (一) 缓存一致性协议

- 多个处理器从主内存读取同一个数据，如果某个处理器修改了工作内存中的数据，该数据会立即同步到主内存，其他处理器通过总线嗅探机制感知变化并使自己的数据无效。
- **总线嗅探**：每个处理器都监听共享总线上的通信。如果发现某个处理器修改了某个内存地址的数据，它会标记自己缓存中相同地址的数据为“无效”，确保下次访问该数据时从主存中重新读取。

## (二) 线程安全的三大特性

### 1. 原子性（synchronized、lock、原子类 AtomicInteger）

- 一个或多个操作要么全部执行且不被打断，要么都不执行。

### 2. 可见性（volatile、synchronized、lock）

- 一个线程修改了共享变量，其它线程能够立刻得知这个修改。

### 3. 有序性（synchronized、lock、volatile）

- 程序执行的顺序和代码的先后顺序一致。

## (三) volatile 关键字

- volatile 可以保证变量修改对其他线程的可见性，并且禁止本线程内相关指令的重排序，但是不保证原子性。
- volatile 可以保证写操作之后的读操作可以读到最新结果，但是不能保证其他线程的读操作会不会被重排序到本线程写操作之前。
- 应用场景：一写多读、double check locking 中对锁外面的变量使用 volatile。

### 1. 原理

- volatile 底层原理是内存屏障（Memory Barrier）。
- JVM 在 volatile 变量的写指令之后加入写屏障。
- JVM 在 volatile 变量的读指令之前加入读屏障。

### 2. 可见性

- JVM 在写操作之后插入写屏障，保证写屏障之前对该变量的修改，立即刷新到主内存。
- JVM 在读操作之前插入读屏障，强制读屏障之后对该变量的读取，都加载主内存中的最新数据。

### 3. 有序性

- volatile 写操作

- volatile 写前插入 StoreStore 屏障，禁止将前面的写操作排在 volatile 写之后。
- volatile 写后插入 StoreLoad 屏障，禁止将后面的所有操作排在volatile 写之前。

- volatile 读操作

- 禁止后面的所有操作排在 volatile 读之前。

## (四) happens-before 原则

- 如果一个操作 happens-before 另一个操作，那么第一个操作的执行结果将对第二个操作可见，并且第一个操作的执行顺序排在第二个操作之前。
- 两个操作之间存在 happens-before 关系，执行顺序不一定和代码顺序一致。如果重排序之后的执行结果，与按 happens-before 执行的结果一致，那么 JMM 也允许这样的重排序。

**1. 程序顺序规则**

- 一个线程中，按照代码顺序，前面操作的结果对于后续的任意操作可见。

```
new Thread(() -> {
    double pi = 3.14;	// 前两行可以重排序，但是前两行不会被排序到第三行之后。 
    double r = 1.0; 
    double area = pi * r * r; // C
}
```

**2. 解锁规则**

- 一个线程解锁之前的写，对于接下来的**加锁**线程的读可见。

**3. volatile 变量规则**

- 一个线程对 volatile 变量的写，对接下来的**所有**线程的读可见。

**4. 传递性**

- 如果 A happens-before B，且 B happens-before C，那么 A happens-before C。

**5. 线程启动规则**

- 一个线程启动前对变量的写，对该线程内的所有读可见。

**6. 线程结束规则**

- 一个线程结束前对变量的写，对其它线程得知它结束后的读可见（比如 join）。

```
static int x;

Thread t1 = new Thread(()->{
    x = 10;
},"t1");
t1.start();

t1.join();
System.out.println(x);
```

**7. 线程中断规则**

- 线程 t1 中断 t2（interrupt）前对变量的写，对于其他线程得知 t2 被打断后对变量的读可见（通过 t2.interrupted 或 t2.isInterrupted）。

```
static int x;
public static void main(String[] args) {
    Thread t2 = new Thread(()->{
        while(true) {
            if(Thread.currentThread().isInterrupted()) {
                System.out.println(x);
                break;
            }
        }
    },"t2");
    t2.start();
    new Thread(()->{
        sleep(1);
        x = 10;
        t2.interrupt();
    },"t1").start();
    while(!t2.isInterrupted()) {
        Thread.yield();
    }
    System.out.println(x);
}
```

**8. 对变量默认值（0，false，null）的写，对其它线程对该变量的读可见。**

# 四、 悲观锁

## (一) Monitor 监视器/管程

### 1. Monitor

- 每个 Java 对象都可以关联一个 Monitor 对象，每一个 synchronized 的锁对象的对象头中的 MarkWord 字段都保存了一个指向 Monitor 对象的指针。
- **Owner**：存储拥有该 Monitor 对象的线程 ID。
- **EntryList**：BOLCKED 队列，存放因为获取对象锁失败而阻塞的线程。
- **WaitSet**：WAITING 队列，存放因为 wait() 方法等待的线程。

### 2. 对象头

- 普通对象头：Mark Word + Klass Word
- Mark Word

<img src="00-resource/images/Mark Word.png" style="zoom:60%;">

## (二) synchronized（对象监视器锁）

### 1. synchronized 关键字

1. synchronized 是 Java 的关键字，是一种可重入非公平锁，用来保证共享资源访问的**原子性、可见性和有序性**。

- **原子性**：synchronized 是互斥锁，只要有一个线程获得了监视器锁，那么其它线程就都会阻塞，同一时刻只有一个线程获得锁。
- **可见性**：synchronized 在进入同步块时会清空工作内存，从主内存读取最新值，在退出同步块之前会将工作内存的数据刷新到主内存，并且原子地执行所有操作。
- **有序性**：synchronized 不能阻止指令重排序，但是只要共享变量的所有操作都在 synchronized 保护下，happens-before 规则能保证有序性。

2. **同步代码块**

- 锁对象可以是任何对象，但是在多线程下锁对象必须是共享的唯一实例。

```
Object lock = new Object();
synchronized (lock){
    // 同步代码块
}
```

2. **同步方法**：同步方法的锁对象不是自行指定的。

- 实例方法的锁对象是调用者（this），多线程必须使用同一个对象调用才能实现同步。
- 静态方法的锁对象是类的 Class 对象（类名.class），Class 对象全局唯一。

```
// 同步方法，锁住方法中的所有代码。
修饰符 [static] synchronized 返回值 func(){
    // ...
}
```

### 2. Object 类 wait() / notify()

1. **wait()** 和 **notify()** 只能在 synchronized 中使用，且必须**按顺序成对出现**。

```
// 等价于 wait(0,0)。使当前线程等待，直到被其它线程 notify 唤醒，或被中断。
public final void wait();
public final void wait(long timeoutMillis);
public final native void notify();		// 随机唤醒一个等待的线程
public final native void notifyAll();	// 唤醒所有等待的线程
```

2. **wait(long)** 如果当前线程不是监视器锁的持有者，会抛出`IllegalMonitorStateException`。如果是，会**释放锁对象的监视器锁**，阻塞当前线程，并将当前线程放到对象的 **WAITING 队列**中，直到：① 被其他线程用`notify/ notifyAll`唤醒，加入 **BLOCKED 队列**重新竞争CPU；② 或被其他线程用`interrupt()`中断，抛出 `InterruptedException` 异常并清除中断标志；③ 或经过指定时间后，加入 **BLOCKED 队列**重新竞争 CPU；④ 或被虚假唤醒，即不是被 notify、notifyAll、interrupt 唤醒，与操作系统的底层机制有关。
3. **notify()** 如果当前线程不是监视器锁的持有者，会抛出`IllegalMonitorStateException`。否则，唤醒一个在此对象监视器上等待的一个线程，当前线程释放锁后，所有被唤醒的线程开始排队竞争 CPU。
4. **最佳实践**

```
synchronized(lock){
    while(条件不成立){
        lock.wait();
    }
    // 事务代码
}

synchronized(lock){
    lock.notifyAll();
}
```

### 3. 偏向锁、轻量级锁、重量级锁

1. **偏向锁**

- 线程首次使用 CAS 操作将当前线程 ID 设置到锁对象头的 Mark Word，后续重入发现线程 ID 仍是自己表示无竞争，不用进行 CAS 操作，只要不发生竞争，该对象锁就归该线程所有。
- JDK15 开始默认关闭，JDK18 开始废弃无法启用。

**1.1 偏向状态**

- 如果开启偏向锁，对象创建后 Mark Word = 0x05 即最后三位为 101。偏向锁默认有延迟，不会在程序启动时立即生效。
- 如果没有开启偏向锁，对象创建后 Mark Word = 0x01 即最后三位为 001。

**1.2 撤销偏向锁**

1. 调用 hashCode() 方法：因为偏向锁的 Mark Word 高位字段存储线程 ID，无法存储哈希值。轻量级锁、重量级锁会在锁记录中记录哈希值。
2. 其他线程使用锁对象：会将偏向锁升级为轻量级锁。
3. 调用 wait()/notify() 方法：wait() 是重量级锁有的方法。

批量重偏向、撤销

**1.3 批量重偏向**

- 当某个类的对象作为锁对象偏向线程 t1 后，如果这些对象被撤销偏向锁超过 20 次，则后续该类的其他对象都开启重偏向，并且重新偏向到线程 t2，而不是撤销偏向锁。

**1.4 批量撤销**

- 当撤销偏向锁次数超过 40 次，则该类的所有对象都设置为不可偏向。

2. **轻量级锁**

- 对象锁是偏向锁时，如果出现了其他线程竞争对象锁，偏向锁就会升级为轻量级锁，其他线程会通过自旋 + CAS 尝试获取对象锁，不会发生阻塞和上下文切换。
- 当线程获取对象锁时，会创建一个**锁记录 Lock Record**，锁记录中有一个字段指向锁对象，将锁对象头 **Mark Word** 复制到锁记录，并用 **CAS** 操作将锁记录地址和状态 00 复制到锁对象的 Mark Word。

- 如果 CAS 操作成功，锁对象的对象头中存储**锁记录地址和状态 00**。
- 如果 CAS 操作失败，如果是当前线程进行了**锁重入**，就会再创建一条取值为 null 的锁记录，因此 null 锁记录的数量表示锁的重入计数。如果是其它线程已经持有该锁，表明有竞争，进行锁膨胀。

- 当线程释放对象锁时，如果有 null 锁记录，重置锁记录，重入计数减一。如果锁记录不为 null，使用 CAS 操作恢复锁对象头 Mark Word 字段值。

- 如果 CAS 操作成功，则成功完全释放锁。
- 如果 CAS 操作失败，说明轻量级锁已经进行了锁膨胀或升级为重量级锁，进行重量级锁解锁。

3. **锁膨胀**

- 如果对象锁已经是轻量级锁，其他线程可以通过自旋尝试获取锁，如果自旋超过 10 次，就不再自旋而是进入阻塞。
- 其他线程加锁失败后，将为锁对象申请重量级锁，锁对象的 Mark Word 指向 **Monitor** 对象，Monitor 对象的 Owner 指向当前持有锁的线程，然后将自己加入 Monitor 对象的阻塞队列 EntryList。
- 持有锁的线程释放锁时，使用 CAS 操作恢复锁对象头 Mark Word 字段值时会失败。此时，使用对象头中存储的 Monitor 对象地址找到 Monitor 对象，设置 Owner 为 null，唤醒 EntryList 中的线程。

4. **锁消除**

- 如果某段代码被加锁了，但是锁对象经检查后确认不会被共享，那么对象锁就是不必要的，JIT（Java即时编译器）就会将该锁消除，提升效率。

## (三) Lock 锁

### 1. ReentrantLock

1. ReentrantLock 可以保证共享资源的**原子性、可见性和有序性**。lock() 和 unlock() 方法之间的代码块也是临界区， 同一时刻只有一个线程可以获得锁；线程获得锁时会先清空工作内存读取共享变量最新值，在释放锁时会把工作内存的数据刷新到主内存中；有序性由 happens-before 规则保证。
2. **可重入锁**

- ReentrantLock 是一种基于 AQS 实现的**可重入锁**。当前线程持有锁后重复 lock() 会导致 `state + 1`，最大可重入次数是 `2^31-1`；unlock() 时只有 state 减为 0，才会将 `exclusiveOwnerThread` 设置为 null 并执行 `LockSupport.unpark` 真正释放锁。

3. **lock 与 unlock**

```
ReentrantLock([boolean]);	// 无参构造默认创建不公平锁，但是可以传递参数创建为公平锁。
public void lock();		// 获得锁
public void lockInterruptibly();	// 除非当前线程被中断，否则获取锁。
public boolean tryLock(); 
public boolean tryLock(long timeout, TimeUnit unit); 
public void unlock();	// 释放锁
```

- **lock()** 如果锁未被持有，则通过 CAS 获得锁并立即返回，将 state 设置为 1。如果当前线程已经持有该锁，则`state + 1`并立即返回。如果锁被另一个线程持有，则调用 `LockSupport.park()` 使当前线程进入`WAITING`状态，一直睡眠直到获得锁为止。
- **tryLock()** 如果锁被另一个线程持有，则立即返回 false 或者经过指定时间后返回 false。不带时间的 tryLock 无视公平策略立即获取锁，带时间的 tryLock 按公平策略参与排序。
- **unlock()** 调用`tryRelease()`，先检查当前线程是不是锁的持有者，如果不是则抛出 `IllegalMonitorStateException` 异常；如果是则 state -1。如果 state 减为 0 则将 `exclusiveOwnerThread` 设置为 null 释放锁，并调用`LockSupport.unpark`唤醒一个等待线程。

4. 可打断模式

- `lockInterruptibly()/ tryLock(long, TimeUnit)`方法获取锁时是可打断的，如果线程获取锁失败，在等待过程中，可以被其他线程调用`interrupt()`中断，当前线程会抛出`InterruptedException` 异常并清除中断标志。
- lock() 获取锁失败，在等待过程中是无法被打断的，一直等待直到获得锁。

### 2. Condition 条件变量

- **Condition** 必须与 Lock 的实现类结合使用，其中 Lock 取代了 synchronized，Condition 取代了 Object 的监视器（wait、notify），每个 Condition 对象都有自己的等待队列，可以实现精准唤醒。

1. **await 和 signal**

- await 和 signal 可以不按顺序调用，但是每一个 await 之后都必须有一个 signal，否则调用 await 的线程可能无限等待。

```
void await();		// 阻塞线程，直到被通知，或被中断，或经过指定的时间。
long awaitNanos(long);	// 等待指定纳秒，返回剩余等待时间
void awaitUninterruptibly();	// 阻塞过程中不可打断。
void signal();		// 唤醒一个等待的线程。
void signalAll();	// 唤醒所有等待的线程。
```

- **await()** 如果当前线程未持有 Lock 锁，会抛出 `IllegalMonitorStateException` 异常。如果是，将当前线程加入 **Condition 的等待队列**，调用`tryRelease()`将 state 直接减为 0 释放 Lock 锁，调用`LockSupport.unpark`唤醒一个等待锁的线程，并用 `LockSupport.park` 使当前线程进入等待状态，一直睡眠直到：① 被其他线程用 `signal/signalAll` 唤醒，然后加入**锁的阻塞队列**竞争锁；② 或被其他线程用`interrupt()`中断，抛出 `InterruptedException` 异常并清除中断标志；③ 或经过指定时间后，加入**锁的阻塞队列**重新竞争锁；④ 或被虚假唤醒。
- **signal()** 如果当前线程未持有 Lock 锁，会抛出 `IllegalMonitorStateException` 异常。如果是，会移除 Condition 的等待队列头节点，并加入 Lock 锁的阻塞队列。当前线程释放锁之后，其他线程开始竞争锁。

### 3. ReentrantReadWriteLock

- 读写锁遵循“读读并发、读写互斥、写写互斥”。
- 适合读多写少的场景。
- 默认创建非公平锁。

```
ReentrantReadWriteLock([boolean]);
```

1. 底层

- 读锁和写锁使用的是同一个同步器 Sync，因此阻塞队列、state 等也是同一个。
- state 低16位表示写锁的状态，高16位表示读锁的状态。
- 读锁/写锁重入：持有读锁/写锁的线程可以再次获取读锁/写锁。
- 读写锁之间的重入：**写锁可以降级，读锁不能升级**

- 持有写锁的线程可以获取读锁，并且解释释放写锁仍持有读锁。
- 持有读锁的线程不能获取写锁，并且试图获取写锁可能会导致死锁。

2. **WriteLock**

- **lock()** 如果写锁和读锁都未被其他线程持有，则获取写锁，持有计数器 +1 并立即返回。否则，当前线程被阻塞直到获取写锁。
- **unlock()** 使 state 低 16 位 -1，如果减为 0 则释放写锁。如果当前线程不是锁的持有者，则抛出 `IllegalMonitorStateException` 异常。
- 写锁支持 Condition。

3. **ReadLock**

- **lock()** 如果写锁未被其他线程持有，无论有没有其他线程获得读锁，都可以成功获取读锁，持有计数器 +1 并立即返回。如果写锁被其他线程占有，当前线程被阻塞直到获取读锁。
- **unlock()** 使 state 高 16 位 -1，如果减为 0 则释放读锁。如果当前线程不是锁的持有者，则抛出 `IllegalMonitorStateException` 异常。
- 读锁不支持 Condition。

## (四) LockSupport

1. LockSupport 为每个线程维护一个许可，该许可相当于布尔值，没有数量，只有**两种状态：有许可、无许可**，并且初始状态为“无许可”。
2. LockSupport 为每个线程维护一个 **Blocker**，它记录了线程阻塞`park`的原因，可以在 park() 中传递 blocker 参数，通常在使用 LockSupport 的类中传递一个 this。

```
private static void setBlocker(Thread t, Object arg);
public static Object getBlocker(Thread t);
```

3. **park() 和 unpark()**

- 可以在线程的任何地方调用 **park** 和 **unpark**，并且无论调用先后，只要成对出现线程就能顺利执行。

```
public static void park();
public static void unpark(Thread thread);
```

- **park()** 会获取许可，如果许可可用，消耗许可并立即返回。如果许可不可用，则阻塞当前线程，直到：① 被其他线程用 unpark 唤醒；② 被其他线程中断并设置中断状态；③ 如果中断标记为 true，park 会失效；④ 虚假唤醒。
- **unpark()** 会为指定线程提供许可。如果线程已经调用过 park，则立即唤醒该线程；如果线程没有调用 park，则该线程调用 park 时不会阻塞。

# 五、乐观锁（无锁）

- 乐观锁一般使用版本号机制或 CAS + volatile 变量实现。

## (一) 版本号

- 一般设置一个版本号字段，每次修改数据都要更新版本号。事务提交修改时，当前版本号与读取时版本号一致修改成功；否则，重试直到成功。
- AtomicStampedReference 检查的时候同时检查当前引用是否等于预期引用且当前版本是否等于预期版本。

### 1. StampedLock

- StampedLock 在使用读锁、写锁时必须配合戳 stamp 使用。
- StampedLock 不支持条件变量、不支持重入。
- 适合读多写少且线程不会重入的情况。

```
long stamp = lock.readLock();
lock.unlockRead(stamp);
long stamp = lock.writeLock();
lock.unlockWrite(stamp);
```

1. **写锁**：独占锁，一把锁只能被一个线程获得。当一个线程获取写锁后，其他请求读锁和写锁的线程必须等待。类似于 `ReentrantReadWriteLock` 的写锁，不过这里的写锁是不可重入的。
2. **读锁**：共享锁，没有线程获取写锁的情况下，多个线程可以同时持有读锁。如果己经有线程持有写锁，则其他线程请求获取该读锁会被阻塞。类似于 `ReentrantReadWriteLock` 的读锁，不过这里的读锁是不可重入的。
3. **乐观读**

- StampedLock 支持`tryOptimisticRead()`方法，读取完毕后进行校验 `validate(stamp)`，如果校验通过，表示期间没有写操作，数据可以安全使用；如果校验没通过，需要获取读锁，重新读取数据。

```
long stamp = lock.tryOptimisticRead();
dataRead();						// 读取数据
if(lock.validate(stamp)){		// 校验戳
    return data;				// 数据可用
}
try{							// 数据不可用
    stamp = lock.readLock();	// 锁升级
    dataRead();					// 读取数据
    return data;			
} finally {
    lock.unlockRead(stamp);	
}
```

## (二) CAS（compareAndSet）

- CAS 操作底层使用的是 CPU 的一条原子指令，当内存中的值与预期值相同时，则进行更新并返回 true，否则返回 false。
- CAS 操作必须是原子操作，Java 的 CAS 操作是调用 Unsafe 类中的 CAS 操作，而 Unsafe 中的 CAS 操作底层是通过一条原子的机器指令实现的。
- 通常为了保证 CAS 操作的共享变量的可见性，都需要使用 volatile 修饰。

```
public final native boolean compareAndSetInt(
    Object o, 		// 需要修改的对象
    long offset,	// 字段在对象中的偏移量
    int expected,	// 预期值
    int x			// 更新值
);
```

- 缺点

- ABA 问题。
- 自旋开销大。
- 只能保证一个变量的原子性操作。

## (三) 原子类

1. **原子包装类**

- AtomicInteger、AtomicBoolean、AtomicLong

2. **原子引用**

- **AtomicReference**

- 主线程只能判断共享变量与最初值是否相同，但是不能感知从 A 改到 B 又改回 A 的情况。（**ABA问题**）

- **AtomicStampedReference**

- 给原子引用增加一个版本号，追踪原子引用的更改过程，可以知道被更改过几次。

- **AtomicMarkableReference**

- 给原子引用增加一个布尔值，可以检测原子引用是否被修改过。

3. **原子数组**

- AtomicIntegerArray、AtomicLongArray、AtomicReferenceArray

4. **原子字段更新器**

- AtomicReferenceFieldUpdater、AtomicIntegerFieldUpdater、AtomicLongFieldUpdater
- 使用字段更新器可以对 volatile 修饰的变量进行原子操作，如果变量不是 volatile 的会出现异常。

5. **原子累加器**

- LongAdder、DoubleAdder
- 相比于使用 AtomicLong 进行累加，LongAdder 会在有竞争时设置多个累加单元，默认是有2个，最多不会超过CPU核心数，最后将结果汇总。不同线程累加时可以操作不同的 Cell 变量，减少了 CAS 重试失败的次数。
- **缓存行伪共享**

- 因为 Cell 是数组，在内存中是连续存储的，一个缓存行可以存放多个 Cell 对象，为了避免一个线程对 Cell 对象进行修改导致对方的缓存行失效，添加 Contended 注解解决。
- Contended 注解原理是在使用该注解的对象或者字端前后各增加 128B 的 **padding**，不同的 Cell 对象就会被读到不同的缓存行。

# 六、线程通信

## (一) synchronized + Object.wait()/notify()

## (二) Lock + Condition.await()/signal()

## (三) LockSupport.park()/unpark()

## (四) volatile 变量

## (五) BlockingQueue/SynchronousQueue

## (六) Semaphore 信号量

- Semaphore 实例维护一组许可，用来限制同一时间访问某种资源的线程数量。
- 可以在线程的任何地方调用 **acquire** 和 **release**，但是必须成对使用，并且不能随意改变先后顺序，否则可能无法按预期控制并发访问资源的线程数量。
- Semaphore 默认采用不公平的同步器，也可以通过参数创建公平同步器。

```
public Semaphore(int permits);	// 使用给定的值初始化许可证数量。
public void acquire();			
public boolean tryAcquire();
public boolean tryAcquire(long timeout, TimeUnit unit);
public void release();			// 释放一个许可证，许可证 +1。
```

- **acquire()** 获取 1/n 个许可，如果有足够的许可可用，获取许可并立即返回。如果不足，当前线程会被加入 Semaphore 实例的等待队列，然后调用`park`使当前线程进入等待状态，一直睡眠直到：① 被其他线程用 release 唤醒；② 被其他线程中断，抛出 `InterruptedException` 异常。
- **tryAcquire()** 会获取 1/n 个许可，如果有足够的许可可用，获取许可并立即返回 true。如果不足，立即返回 false，不会阻塞线程。不带时间的 tryAcquire 不遵守公平策略。
- **tryAcquire(long, TimeUnit)** 会获取 1/n 个许可，如果有足够的许可可用，获取许可并立即返回 true。如果不足，当前线程会被加入 Semaphore 实例的等待队列，然后调用`park`使当前线程进入等待状态，一直睡眠直到：① 被其他线程用 release 唤醒，如果有足够许可证则获取并返回 true，否则继续等待；② 或被其他线程中断，抛出 `InterruptedException` 异常并清除中断标志；③ 或经过指定时间后，返回 false。带时间的 tryAcquire 遵守公平策略。
- **release()** 会释放 1/n 个许可证，每次释放许可证都有可能立即释放等待队列中一个线程。

## (七) CountDownLatch

- CountDownLatch 实例维护一个倒数计数器，`await`让线程阻塞，每次调用`countDown`使得计数器 -1，当计数器归零时，所有在该 CountDownLatch 实例上等待的线程都会被唤醒，此时再有其他线程调用 await 都可以直接返回。

```
public CountDownLatch(int count); 	// 使用给定的值初始化计数器。 
public void await(); 				// 使线程阻塞，直到计数器归0，自动唤醒该线程，或线程被中断。 
public void await(long , TimeUnit); // 使线程阻塞，直到计数器归0，自动唤醒该线程，或线程被中断，或者经过了指定的时间。 
public void countDown();			// 每次调用使计数器 -1。 
```

- **await()** 如果计数器 =0，则直接返回。否则，当前线程会被加入 CountDownLatch 实例的等待队列，然后调用`park`使当前线程进入等待状态，一直睡眠直到：① 其他线程调用 countdown 使计数器减为 0；② 被其他线程中断，抛出 `InterruptedException` 异常；③ 或等到指定时间。
- **countDown()** 如果当前计数 =0，则不会发生任何事。如果当前计数大于 0，则计数器 -1，如果新计数为 0，就立即唤醒所有等待线程。

## (八) CyclicBarrier

- CyclicBarrier 可以使指定 parties 个线程等待彼此，当所有线程全部到达一个共同的屏障，所有阻塞线程才会继续运行。
- CyclicBarrier 创建时可以传递一个 Runnable 类型的屏障任务，每次当所有线程都到达屏障后，最后一个到达屏障的线程执行该屏障任务。

```
public CyclicBarrier(int parties);	
public CyclicBarrier(int parties, Runnable barrierAction);	
public int await();		// 使线程阻塞，直到所有线程均到达屏障。
public int await(long timeout, TimeUnit unit);
public void reset();
private void nextGeneration();	// 恢复 count 计数为 parties，创建新的generation，开启新的轮次
```

- **await()** 首先，调用 CyclicBarrier 实例持有的`ReentrantLock`实例的 lock 方法加锁。然后执行`--count` 计算本轮次还剩多少线程没有到达屏障。如果 count 减为 0 即所有线程均到达屏障，再判断是否设置了屏障任务，如果有则执行屏障任务。最后通过 CyclicBarrier 实例持有的 Condition 变量执行 `signalAll` 方法唤醒所有等待线程。如果 count 没有减为 0，调用 Condition 变量的 `await`方法释放 lock 锁，睡眠直到：① 最后一个线程到达屏障，则所有线程都会被唤醒；② 当前线程被中断，抛出 `InterruptedException` 异常并清除中断标志，调用`**breakBarrier**()`方法；③ 当前线程等待指定时间后，抛出`TimeoutException`异常，调用`**breakBarrier**()`方法；④ 等待屏障的**其他线程**被**中断**、**超时**、调用 **reset()**，会抛出`BrokenBarrierException`异常。
- **reset()** 首先调用`breakBarrier()`破坏当前轮次，然后唤醒所有等待线程，这些被唤醒的线程会抛出`BrokenBarrierException`异常，由使用这些线程自己决定是否进入新的轮次。然后调用`nextGeneration()`恢复 count 并创建新的 generation。

# 七、线程池

## (一) 线程池状态

|   |   |   |   |   |
|---|---|---|---|---|
|状态|高3位|接受新任务|处理阻塞队列任务|说明|
|RUNNING|111|√|√||
|SHUTDOWN|000|×|√|不再接受新任务，但会处理阻塞队列剩余任务。|
|STOP|001|×|×|中断正在执行的任务，并抛弃阻塞队列任务。|
|TIDYING|010|||任务执行完毕，活动线程数为 0 即将进入终结状态。|
|TERMINATED|011||||

- ThreadPoolExecutor 使用 int 变量 **ctl** 的高 3 位表示线程池状态，低 29 位表示线程数量，一次 CAS 操作就可以进行赋值。

## (二) ThreadPoolExecutor 自定义线程池

### 1. 自定义线程池

```
public ThreadPoolExecutor(
    int corePoolSize, 
    int maximumPoolSize, 
    long keepAliveTime, 
    TimeUnit unit, 
    BlockingQueue<Runnable> workQueue, 
    ThreadFactory threadFactory, 
    RejectedExecutionHandler handler
);
```

1. **核心线程数和最大线程池大小**

- 当通过 **execute(Runnable)** 方法提交新任务时，如果运行的线程少于 **corePoolSize**，无论是否有空闲线程，都创建新的核心线程。如果总线程数达到 **corePoolSize** 并且没有空闲线程，任务加入工作队列。如果队列容量有限且队列已满，则创建非核心线程执行任务，如果线程数达到 **maximumPoolSize**，则按照拒绝策略拒绝该任务。
- 如果设置`corePoolSize = maximumPoolSize`或使用无界队列，就可以创建一个固定大小的线程池。

2. **超时策略**

- 当线程池中线程数超过 corePoolSize，非核心线程的空闲时间超过 **keepAliveTime** 个 **unit** 后就会被线程池回收。
- 默认情况下，超时策略只应用于非核心线程。在保活时间 `keepAliveTime!=0` 的前提下，通过`allowCoreThreadTimeOut(boolean)` 方法可以将超时策略应用于核心线程，也可以取消。

3. **工作队列**

- 任何实现 **BlockingQueue** 接口的队列都可以当作传输和保存提交的任务的工作队列。
- **同步队列**

- SynchronousQueue 不存储元素，插入操作会直接阻塞直到有对应的取操作。每次有新任务都直接移交给线程，如果没有空闲线程会直接创建一个新线程。
- 该策略避免了在处理可能具有内部依赖关系的请求集时出现死锁。
- 如果命令继续以平均更快的速度到达而无法处理，该策略可能导致线程池无限增长。

- **无界队列**

- LinkedBlockingQueue 等无界队列在所有核心线程都忙碌时，会将所有新任务都加入工作队列，永远不会创建超过 corePoolSize 个线程，也永远都不会拒绝任务。
- 如果每个任务都完全相互独立，该策略比较合适，在平滑处理瞬时请求突发时很有用。
- 如果命令继续以平均更快的速度到达而无法处理，该策略可能导致工作队列无限增长。

- **有界队列**

- ArrayBlockingQueue 等有界队列与有限的 maximumPoolSize 一起使用防止资源耗尽或者 OOM。当所有核心线程都忙碌时，会将所有新任务都加入工作队列。如果工作队列已满，则创建线程处理其余任务。如果线程数超过 **maximumPoolSize**，则拒绝该任务。
- 大队列小池可以最小化 CPU 使用率、上下文切换的开销等，但是吞吐量也随着降低。
- 小队列大池可以提高 CPU 使用率，但如果遇到无法接受的调度开销，也会降低吞吐量。

4. **线程工厂**

- ThreadFactory 创建新线程，默认使用 `Executors.defaultThreadFactory()`，它创建的线程具有相同的优先级（NORM_PRIORITY=5）和非守护线程状态。

5. **拒绝策略**

- 当线程池已关闭或线程池的 **maximumPoolSize** 和 **workQueue** 容量都有限并且都达到上限时，提交新的任务会被拒绝。可以通过实现`RejectedExecutionHandler`接口自定义拒绝策略。
- **AbortPolicy**：默认策略。丢弃当前任务并抛出`RejectedExecutionException` 异常。
- **DiscardPolicy**：丢弃当前任务，但是不抛出异常。不推荐。
- **DiscardOldestPolicy**：丢弃队列中等待最久（队头）的任务，然后把提交的新任务加入队列。
- **CallerRunsPolicy**：调用 execute() 提交任务的线程会直接调用`run()`方法，将任务当作普通函数执行。

### 2. 提交任务

1. `void execute(Runnable command)` 没有返回结果。如果执行任务过程中发生异常，只能在任务内部捕获或者自定义 `ThreadFactory` 并设置一个未捕获异常处理器，否则会导致该线程终止，线程池会创建新的线程替换该线程。

2. `submit()` 提交任务。如果执行过程中发生异常，异常会被封装在返回值 Futrue 中，调用 Future.get() 抛出`ExecutionException`异常。如果任务是 Runnable，在不发生异常的情况，返回值返回 result 或 null，与业务逻辑无关。

```
public <T> Future<T> submit(Callable<T> task);
public Future<?> submit(Runnable task);
public <T> Future<T> submit(Runnable task, T result);
```

3. `invokeAll`会提交所有任务，并返回对应的 future 列表。如果传递超时时间，当所有任务都完成或者超时后，返回所有结果，未完成的任务都会被取消。

```
public <T> List<Future<T>> invokeAll(Collection<? extends Callable<T>> tasks) throws InterruptedException;
public <T> List<Future<T>> invokeAll(Collection<? extends Callable<T>> tasks, long timeout, TimeUnit unit) throws InterruptedException;
```

4. `invokeAny`提交所有任务。如果有任务在超时时间之前完成，取消所有未完成任务，并返回这个任务的结果。如果有任务在超时前发生异常 / 没有任务在超时之前完成，取消所有未完成任务，抛出`ExecutionException`异常。

```
// 提交 tasks 中所有任务，哪个任务先成功执行完毕，返回此任务执行结果，其它任务取消
<T> T invokeAny(Collection<? extends Callable<T>> tasks)
        throws InterruptedException, ExecutionException;

// 提交 tasks 中所有任务，哪个任务先成功执行完毕，返回此任务执行结果，其它任务取消，带超时时间
<T> T invokeAny(Collection<? extends Callable<T>> tasks,
                long timeout, TimeUnit unit)
        throws InterruptedException, ExecutionException, TimeoutException;
```

### 3. 关闭线程池

1. `void shutdown()`将线程池状态变为 `SHUTDOWM`，不接受新任务，剩余任务全部执行完毕后关闭线程池。如果尝试添加任务，会抛出`RejectedExecutionException`异常。
2. `List<Runnable> shutdownNow()`将线程池状态变为 `STOP`，不再接受新任务，立即中断当前任务，直接尝试关闭线程池并返回剩余未执行任务。
3. `boolean isShutdown()`判断线程池是否关闭，只要不是`RUNNING`状态都返回 true。
4. `boolean isTerminated()`判断线程池状态是否为`TERMINATED`。
5. `boolean awaitTermination(long,TimeUnit)`等待线程池 TERMINATED，直到超时返回 false 或者线程池 TERMINATED 返回 true。

### 4. 线程池预热

- `prestartCoreThread()`：启动一个核心线程，等待任务。如果已达到核心线程数，返回 false，否则返回 true；
- `prestartAllCoreThreads()`：启动所有的核心线程，并返回启动成功的核心线程数。

## (三) Executors 默认线程池

- Executors 类提供静态方法创建常用的线程池，ExecutorService 实现类就是不同线程池的模板类。

1. **无界线程池 newCachedThreadPool**

- 核心线程数是 0， 最大线程数是 Integer.MAX_VALUE，非核心线程的保活时间 60s。
- 工作队列使用 `SynchronousQueue` 实现，不存储元素，每有一个新任务都会创建一个新线程。
- 适合任务数比较密集，但每个任务执行时间较短的情况。

```
public static ExecutorService newCachedThreadPool() {
    return new ThreadPoolExecutor(0, Integer.MAX_VALUE,
                                  60L, TimeUnit.SECONDS,
                                  new SynchronousQueue<Runnable>());
}
```

2. **固定大小线程池 newFixedThreadPool**

- 线程池最多只包含 nThreads 个核心线程，工作队列使用无界队列。
- 适用于任务量已知，相对耗时的任务。

```
public static ExecutorService newFixedThreadPool(int nThreads) {
    return new ThreadPoolExecutor(nThreads, nThreads,
                                  0L, TimeUnit.MILLISECONDS,
                                  new LinkedBlockingQueue<Runnable>());
}
```

3. **单线程池 newSingleThreadExecutor**

- 线程池只包含 1 个核心线程，工作队列使用的无界队列。
- 装饰器模式：通过包一层`FinalizableDelegatedExecutorService`，只对外暴露了 ExecutorService 接口，因此不能调用 ThreadPoolExecutor 中特有的方法，不能修改线程池核心参数。

- 与`Executors.newFixedThreadPool(1)` 相比，对外暴露的接口不同，newFixedThreadPool 可以强转为 ThreadPoolExecutor 类型，然后修改线程池的核心参数。

```
public static ExecutorService newSingleThreadExecutor() {
    return new FinalizableDelegatedExecutorService
        (new ThreadPoolExecutor(1, 1,
                                0L, TimeUnit.MILLISECONDS,
                                new LinkedBlockingQueue<Runnable>()));
}
```

4. **任务调度线程池 newScheduledThreadPool**

- ScheduledThreadPoolExecutor 核心线程数 corePoolSize，最大线程数 Integer.MAX_VALUE，非核心线程保活时间为 10ms。
- 工作队列使用 `DelayedWorkQueue`，按照设置的任务实际执行时间排序。

```
public ScheduledThreadPoolExecutor(int corePoolSize) {
    super(corePoolSize, Integer.MAX_VALUE,
          DEFAULT_KEEPALIVE_MILLIS, MILLISECONDS,
          new DelayedWorkQueue());
}
```

- **schedule()** 提交任务后延迟指定时间后执行任务。

```
public ScheduledFuture<?> schedule(Runnable command, long delay, TimeUnit unit);
public <V> ScheduledFuture<V> schedule(Callable<V> callable, long delay, TimeUnit unit);
```

- **scheduleAtFixedRate**() 提交任务后延迟`initialDelay`时间后执行任务，然后每次间隔`period`执行一次该任务，后续时间计算是以上一次任务开始时间为基准。

```
public ScheduledFuture<?> scheduleAtFixedRate(Runnable command, long initialDelay, long period, TimeUnit unit);
```

- **scheduleWithFixedDelay**() 提交任务后延迟`initialDelay`时间后执行任务，然后每次间隔`delay`执行一次该任务，后续时间计算是以上一次任务结束时间为基准。

```
public ScheduledFuture<?> scheduleWithFixedDelay(Runnable command, long initialDelay, long delay, TimeUnit unit);
```

## (四) Fork/Join 线程池

- 分治思想，适用于能够进行任务拆分的 cpu 密集型运算。
- Fork/Join 在分治思想的基础上加入多线程，将任务分解和和合并交给不同的线程完成，默认会创建与CPU核心数大小相同的线程池。
- Fork/Join 线程池的任务需要继承 **RecursiveTask**（有返回值）或 **RecursiveAction**（没有返回值）。

# 八、ThreadLocal

- ThreadLocal 为存储的泛型对象在每个线程中都创建了一个副本，副本只属于当前线程，该副本在不同线程中是独立的，实现了线程之间的隔离。
- **Thread** 中有一个 ThreadLocal.**ThreadLocalMap** 类型的成员变量 `threadLocals`，ThreadLocalMap 中有一个名为 table 的 **Entry[]** 数组。Entry 是一个继承自 WeakReference 的静态内部类，Entry 保存的的 Key 是 ThreadLocal 对象的弱引用，**value** 是 ThreadLocal 中存储的泛型对象。

```
static class Entry extends WeakReference<ThreadLocal<?>> {
    Object value;
    Entry(ThreadLocal<?> k, Object v) {
        super(k);
        value = v;
    }
}
```

## (一) 内存泄漏

1. **内存泄漏的原因**

- 没有手动删除 Entry，并且线程长时间运行，有可能导致内存泄漏。
- ThreadLocalMap 的 Entry 继承自 **WeakReference**。其中 key 是 ThreadLocal 对象的**弱引用**，当外部不再持有该 ThreadLocal 对象的强引用时，下次 GC 时就会将 ThreadLocal 对象回收，key 就会变成 null。但是变量副本 value 是强引用，只要线程仍然存活，value 就一直存在引用链：CurrentThread -> ThreadLocalMap -> Entry[] -> Entry -> value -> 堆中的对象。因为 ThreadLocal 对象被回收，而且 table 是私有变量，导致该 Entry 以及 value 永远无法访问。

## (二) InheritableThreadLocal

- JDK1.2 提供的一个类，继承自 `ThreadLocal` 。使用 `InheritableThreadLocal` 时，会在创建子线程时，令子线程继承父线程中的 `ThreadLocal` 值，但是无法支持线程池场景下的 `ThreadLocal` 值传递。

## (三) TransmittableThreadLocal

TTL 巧妙地利用了**装饰器模式**对任务（`Runnable`/`Callable`）或线程池（`Executor`）进行增强，将上下文的传递时机从“线程创建时”延迟到了“任务提交与执行时”。

TTL 的核心逻辑可以概括为三个阶段（CRR）：

- **Capture（捕获）**：在提交任务（如调用 `execute`）的一瞬间，`TtlRunnable` 会调用 `TransmittableThreadLocal.Transmitter.capture()`。它通过内部维护的 `holder` 集合，抓取当前父线程中所有活跃的 TTL 变量并存入快照。
- **Replay（回放）**：在线程池的工作线程执行 `run()` 方法前，调用 `replay()`。它将快照中的值 `set` 到当前工作线程中，并备份该线程原有的旧值。
- **Restore（恢复）**：任务执行结束后，调用 `restore()`。它根据备份将工作线程恢复到执行前的状态，防止上下文污染或内存泄漏。

# 九、模式

## (一) 两阶段终止模式

<img src="00-resource/images/两阶段终止模式.png" style="zoom:75%;">

1. 使用 `interrupt()`实现

```
class TPTInterrupt {
    private Thread thread;
    
    public void start() {
        thread = new Thread(() -> {
            while (true) {
                Thread current = Thread.currentThread();
                if (current.isInterrupted()) {	// 2. 第二阶段：检测到中断信号
                    postprocess();		// 后置处理，例如：释放资源等
                    break;
                }
                try {
                    Thread.sleep(1000);
                    process();			// 业务代码
                } catch (InterruptedException e) {	// 执行业务过程中被打断
                    current.interrupt();
                }
            }
        }, "监控线程");
        
        thread.start();
    }

    public void stop() {
        thread.interrupt();		// 1. 第一阶段：其他线程向该线程发送中断信号
    }
}
```

2. 使用`volatile`实现

```
class TPTVolatile {
    private Thread thread;
    private volatile boolean stop = false;
    
    public void start(){
        thread = new Thread(() -> {
            while(true) {
                Thread current = Thread.currentThread();
                if(stop) {				// 2. 第二阶段：检测到中断信号
                    postprocess();		// 后置处理，例如：释放资源等
                    break;
                }
                try {
                    Thread.sleep(1000);
                    process();			// 业务代码
                } catch (InterruptedException e) {
                }
            }
        },"监控线程");
        
        thread.start();
    }
    
    public void stop() {
        stop = true;			// 1. 第一阶段：其他线程向该线程发送中断信号
        thread.interrupt();
    }
}
```

## (二) 同步模式——保护性暂停

- 适用于需要将结果从一个线程传递到另一个线程，可以让他们关联同一个结果守护类 GuardedObject。
- join、Future 的实现就是使用的保护性暂停模式。

### 1. 超时控制

```
class GuardedObject {
    private Object response;
    private final Object lock = new Object();

    public Object get(long millis) {
        synchronized (lock) {
            long begin = System.currentTimeMillis();
            long timePassed = 0, waitTime = 0;
            while (response == null) {
                waitTime = millis - timePassed;
                if (waitTime <= 0) {		// 超时
                    break;
                }
                try {
                    lock.wait(waitTime);	// 等待结果或被中断
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
                timePassed = System.currentTimeMillis() - begin;
            }
            return response;
        }
    }

    public void complete(Object response) {
        synchronized (lock) {
            this.response = response;
            lock.notifyAll();
        }
    }
}
```

### 2. 多任务实现

- 通过中间类 Fultures 实现解耦合和支持多任务。

```
class Futures {
    private static Map<Integer, GuardedObject> boxes = new Hashtable<>();
    private static int id = 1;

    private static synchronized int generateId() {
        return id++;
    }

    public static GuardedObject getGuardedObject(int id) {
        return boxes.remove(id);
    }

    public static GuardedObject createGuardedObject() {
        GuardedObject go = new GuardedObject(generateId());
        boxes.put(go.getId(), go);
        return go;
    }

    public static Set<Integer> getIds() {
        return boxes.keySet();
    }
}
```

## (三) 同步模式——犹豫模式

- Balking （犹豫）模式用在一个线程发现另一个线程或本线程已经做了某一件相同的事，那么本线程就无需再做了，直接结束返回。

```
public class MonitorService {
    private Thread monitor;
    private volatile boolean stop = false;
    private volatile boolean started;
    
    public void start() {
        synchronized (this) {
            if (started) {
                return;
            }
            started = true;
        }
        monitor = new Thread(() -> {...},"monitor");
        monitor.start();
    }
    
    public void stop(){
        stop = true;
        monitor.interrupt();
    }
}
```

## (四) 异步模式——生产者消费者

## (五) 异步模式——工作线程

- 让有限的工作线程处理无限多的任务，体现了享元模式。典型实现：线程池。
- 可以将不同类型的任务交给不同的线程池处理，避免饥饿。