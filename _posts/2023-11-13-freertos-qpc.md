---
title: "为 ARM Cortex-M0 平台移植 FreeRTOS + QP/C"
author: Jinkai
date: 2023-11-13 08:00:00 +0800
published: true
categories: [教程]
tags: [FreeRTOS, QPC, ARM]
---

## 概要

本文将介绍如何在 ARM 平台上移植 FreeRTOS，并创建一个线程用于 QP/C 中的 QV 内核运行，项目构建使用 CMake+GCC 环境。

## FreeRTOS 移植

FreeRTOS 提供了多套移植，这里选用`GCC/ARM_CM0`。

主要需要修改的是`FreeRTOSConfig.h`配置文件，主要是把动态内存分配功能关闭了，使内存更加可控：

```c
/*
 * FreeRTOS V202212.00
 * Copyright (C) 2020 Amazon.com, Inc. or its affiliates.  All Rights Reserved.
 *
 * Permission is hereby granted, free of charge, to any person obtaining a copy
 * of this software and associated documentation files (the "Software"), to deal
 * in the Software without restriction, including without limitation the rights
 * to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 * copies of the Software, and to permit persons to whom the Software is
 * furnished to do so, subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be included in
 * all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 * IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 * FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 * AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 * LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 * OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 * SOFTWARE.
 *
 * https://www.FreeRTOS.org
 * https://github.com/FreeRTOS
 *
 */

#ifndef FREERTOS_CONFIG_H
#define FREERTOS_CONFIG_H

/*-----------------------------------------------------------
 * Application specific definitions.
 *
 * These definitions should be adjusted for your particular hardware and
 * application requirements.
 *
 * THESE PARAMETERS ARE DESCRIBED WITHIN THE 'CONFIGURATION' SECTION OF THE
 * FreeRTOS API DOCUMENTATION AVAILABLE ON THE FreeRTOS.org WEB SITE.
 *
 * See http://www.freertos.org/a00110.html
 *----------------------------------------------------------*/

#define configUSE_PREEMPTION             0
#define configUSE_IDLE_HOOK              0
#define configUSE_TICK_HOOK              1
#define configUSE_TICKLESS_IDLE          1
#define configCPU_CLOCK_HZ               1843200
#define configSYSTICK_CLOCK_HZ           1000
#define configTICK_RATE_HZ               ((TickType_t)1000)
#define configMAX_PRIORITIES             (5)
#define configMINIMAL_STACK_SIZE         ((unsigned short)30)
#define configMAX_TASK_NAME_LEN          (5)
#define configUSE_TRACE_FACILITY         0
#define configUSE_16_BIT_TICKS           0
#define configIDLE_SHOULD_YIELD          1
#define configUSE_MUTEXES                1
#define configQUEUE_REGISTRY_SIZE        8
#define configCHECK_FOR_STACK_OVERFLOW   2
#define configUSE_RECURSIVE_MUTEXES      0
#define configUSE_MALLOC_FAILED_HOOK     0
#define configUSE_APPLICATION_TASK_TAG   0
#define configUSE_COUNTING_SEMAPHORES    0
#define configGENERATE_RUN_TIME_STATS    0
#define configSUPPORT_STATIC_ALLOCATION  1
#define configSUPPORT_DYNAMIC_ALLOCATION 0

/* Co-routine definitions. */
#define configUSE_CO_ROUTINES           0
#define configMAX_CO_ROUTINE_PRIORITIES (2)

/* Software timer definitions. */
#define configUSE_TIMERS             1
#define configTIMER_TASK_PRIORITY    (2)
#define configTIMER_QUEUE_LENGTH     3
#define configTIMER_TASK_STACK_DEPTH (40)

/* Set the following definitions to 1 to include the API function, or zero
to exclude the API function. */
#define INCLUDE_vTaskPrioritySet      0
#define INCLUDE_uxTaskPriorityGet     0
#define INCLUDE_vTaskDelete           0
#define INCLUDE_vTaskCleanUpResources 0
#define INCLUDE_vTaskSuspend          0
#define INCLUDE_vTaskDelayUntil       1
#define INCLUDE_vTaskDelay            1

/* Normal assert() semantics without relying on the provision of an assert.h
header file. */
#define configASSERT(x)           \
    if ((x) == 0) {               \
        taskDISABLE_INTERRUPTS(); \
        for (;;)                  \
            ;                     \
    }

/* Definitions that map the FreeRTOS port interrupt handlers to their CMSIS
standard names - or at least those used in the unmodified vector table. */
#define vPortSVCHandler     SVC_Handler
#define xPortPendSVHandler  PendSV_Handler
#define xPortSysTickHandler PBSP_sysTickHandlerCallback

#endif /* FREERTOS_CONFIG_H */
```

注意需要将 xPortSysTickHandler 在内的几个中断处理函数替换为适合自己环境的，具体的配置项可以在[官网](https://www.freertos.org/zh-cn-cmn-s/a00110.html)查看。

## QP/C 移植

这里需要移植的有 QF 框架和 QV 内核，在官方提供的 posix-qv 移植上做些修改即可，主要为如下两个文件：

qf_port.h:

```c
#include "FreeRTOS.h"
#include "task.h"

extern TaskHandle_t qpTask;

#define QACTIVE_EQUEUE_SIGNAL_(me_)               \
    do {                                          \
        QPSet_insert(&QF_readySet_, (me_)->prio); \
        xTaskNotifyGiveIndexed(qpTask, 0);        \
    } while (false)
// 其他部分与posix-qv移植相同
...
```

qf_port.c:

```c
#include "FreeRTOS.h"
#include "task.h"
#include "semphr.h"

// 采用静态分配内存方式
static SemaphoreHandle_t l_pThreadMutex;
static StaticSemaphore_t xSemaphoreBuffer;

// 初始化部分只需初始化互斥锁
void QF_init(void)
{
    /* init the global mutex with the default non-recursive initializer */
    // 静态分配一个非递归锁
    l_pThreadMutex = xSemaphoreCreateMutexStatic(&xSemaphoreBuffer);
}

// 进入临界区，使用互斥锁
void QF_enterCriticalSection_(void)
{
    xSemaphoreTake(l_pThreadMutex, portMAX_DELAY);
}

// 退出临界区
void QF_leaveCriticalSection_(void)
{
    xSemaphoreGive(l_pThreadMutex);
}

// 启动QV内核
int_t QF_run(void)
{
    QF_CRIT_STAT_

    QF_onStartup(); /* invoke startup callback */

    l_isRunning = true; /* QF is running */

    /* system clock tick configured? */

    /* the combined event-loop and background-loop of the QV kernel */
    QF_CRIT_E_();

    /* produce the QS_QF_RUN trace record */
    QS_BEGIN_NOCRIT_PRE_(QS_QF_RUN, 0U)
    QS_END_NOCRIT_PRE_()

    while (l_isRunning) {
        /* find the maximum priority AO ready to run */
        if (QPSet_notEmpty(&QF_readySet_)) {
            uint_fast8_t p = QPSet_findMax(&QF_readySet_);
            QActive *a     = QActive_registry_[p];
            QF_CRIT_X_();

            /* the active object 'a' must still be registered in QF
             * (e.g., it must not be stopped)
             */
            Q_ASSERT_ID(320, a != (QActive *)0);

            /* perform the run-to-completion (RTS) step...
             * 1. retrieve the event from the AO's event queue, which by this
             *    time must be non-empty and The "Vanialla" kernel asserts it.
             * 2. dispatch the event to the AO's state machine.
             * 3. determine if event is garbage and collect it if so
             */
            QEvt const *e = QActive_get_(a);
            QHSM_DISPATCH(&a->super, e, a->prio);
            QF_gc(e);

            QF_CRIT_E_();

            if (a->eQueue.frontEvt == (QEvt *)0) { /* empty queue? */
                QPSet_remove(&QF_readySet_, p);
            }
        }
        else {
            // 当没有事件需要处理时休眠本线程
            while (QPSet_isEmpty(&QF_readySet_)) {
                QF_CRIT_X_();
                ulTaskNotifyTake(pdTRUE, portMAX_DELAY);
                QF_CRIT_E_();
            }
        }
    }
    QF_CRIT_X_();
    QF_onCleanup(); /* cleanup callback */
    QS_EXIT();      /* cleanup the QSPY connection */

    return 0; /* return success */
}

// 停止QV内核，这里需要通过发送一个直达通知解除QV等待事件的状态
void QF_stop(void)
{
    uint_fast8_t p;
    l_isRunning = false; /* terminate the main event-loop thread */

    /* unblock the event-loop so it can terminate */
    p = 1U;
    QPSet_insert(&QF_readySet_, p);
    xTaskNotifyGiveIndexed(qpTask, 0);
}

// 其他部分与posix-qv移植相同
...
```

为了让 QV 正常运行，还需要一个定时器，可以使用多种方式，这里使用 FreeRTOS 自带的定时器实现：

```c
#include "FreeRTOS.h"
#include "timers.h"

Q_DEFINE_THIS_FILE

TimerHandle_t qpcTimer = NULL;
static StaticTimer_t xTimerBuffer;

static void sysTickTimerHandlerCallback(TimerHandle_t xTimerHandle);

void QPC_init(void)
{
    qpcTimer = xTimerCreateStatic(
        "qpTimer", /* Text name for the task.  Helps debugging only.  Not used
                    by FreeRTOS. */
        1,         /* The period of the timer in ticks. */
        pdTRUE,    /* This is an auto-reload timer. */
        NULL,      /* The variable incremented by the test is passed into the
                      timer callback using the timer ID. */
        sysTickTimerHandlerCallback, /* The function to execute when the
                                      timer expires. */
        &xTimerBuffer); /* The buffer that will hold the software timer
                           structure. */
}

void QF_onStartup(void)
{
    if (qpcTimer != NULL) {
        xTimerStart(qpcTimer, 0);
    }
}

void QF_onCleanup(void) {}

// 定时任务回调
static void sysTickTimerHandlerCallback(TimerHandle_t xTimerHandle)
{
    QTIMEEVT_TICK_X(0U, NULL); /* perform the QF clock tick processing */
    static uint16_t secondTick = 0U;
    secondTick += 1U;
    // 秒事件
    if (secondTick == SYSTICKS_PER_SECOND) {
        secondTick = 0U;
        PSCH_EvtAction_sendTimeSecond();
        long milliseconds = 0;
    }
}

void QF_onClockTick(void) {}

/*..........................................................................*/
Q_NORETURN Q_onAssert(char const * const module, int_t const loc)
{
    QF_onCleanup();
    QS_EXIT();
    exit(-1);
}
```

## 为 QP/C 创建一个线程

使用静态分配方式创建线程。

```c
int main(){
    // 静态方式创建TCB线程管理对象
    static StaticTask_t xqpcTCBBuffer;
    // 静态方式创建栈
    static StackType_t uxqpcStackBuffer[configMINIMAL_STACK_SIZE];
    TaskHandle_t qpTask;

    QPC_init();
    qpTask = xTaskCreateStatic(
            // appStart为自己编写的QP应用启动函数
            appStart, /* The function that implements the task. */
            "qpc", /* The text name assigned to the task - for debug only as it
                     is not used by the kernel. */
            configMINIMAL_STACK_SIZE, /* The size of the stack to allocate to
                                         the task. */
            NULL, /* The parameter passed to the task - not used in this simple
                     case. */
            mainQUEUE_RECEIVE_TASK_PRIORITY, /* The priority assigned to the
                                                task. */
            &(uxqpcStackBuffer[0]), /* The buffer to use as the task's stack. */
            &xqpcTCBBuffer /* The variable that will hold that task's TCB. */
        );
    vTaskStartScheduler(); // 开启调度

    for (;;) {
    }
}
```

## 注意事项

### 在 FreeRTOS 中使用条件变量

在一般的操作系统中都会有几个用于同步的原语：互斥量(锁)、条件变量、信号量等([见本文](/posts/operating-systems-24/))。FreeRTOS 省略了条件变量的单独实现，可以用信号量或直达通知来实现条件变量的功能。

示例：

pthread 库中的条件变量使用方法，一般需要配合一个互斥量：

```c
while(iReady):
    pthread_cond_wait(&condVar_, &l_pThreadMutex);
```

在 FreeRTOS 中实现类似的功能：

```c
while(iReady):
{
    xSemaphoreGive(l_pThreadMutex);
    ulTaskNotifyTake(pdTRUE, portMAX_DELAY);
    xSemaphoreTake(l_pThreadMutex, portMAX_DELAY);
}
```

由于没有像 pthread 库那样自动管理互斥量的封装接口，这里使用手动解锁加锁的方式保证休眠前释放线程锁。这里还使用了 FreeRTOS 中的直达通知的方式取代了信号量，据官方称直达通知比信号量快 45%。

## 互斥锁和二值信号量的区别

互斥锁和二值信号量用于实现的功能相同，都是创建一个临界区，但互斥锁的优势是其**优先级继承**特性：当低优先级的任务获得锁进入临界区时，如果有高优先级的任务抢占后等待该锁，则 FreeRTOS 会将该低优先级任务的优先级提高到和等待该锁的高优先级任务相同（优先级继承），以便让低优先级的任务尽快处理完毕来让高优先级任务获得锁，缓解优先级反转问题。

二值信号量创建后默认为上锁状态，互斥锁默认为解锁状态。

### FreeRTOS 内存优化

首先是关闭`FreeRTOSConfig.h`配置文件中的部分配置，减少功能，可以有效减少代码量和内存占用量。

定时器任务需要占用一个线程，不使用定时器可以减少内存占用

空闲任务需要占用一个线程，如果系统中本身就有一个永不阻塞的任务可以关闭此任务，减少内存占用。

引入操作系统后就有了线程概念，每个线程的栈是独立的，也就是说要给每个线程都分配栈空间。栈空间主要用于：

- 保存具有块作用域的局部变量和参数
- 上下文切换时的寄存器保存
- 函数调用时保存返回地址
- 其他特殊情况

当分配栈较小时，需要启用 FreeRTOS 的栈溢出检查功能，防止发生灾难性后果。

## 参考

- [FreeRTOS官方文档](https://www.freertos.org/zh-cn-cmn-s/RTOS_ports.html)
