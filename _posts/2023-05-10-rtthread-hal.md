---
title: "RT-Thread HAL层介绍"
author: Jinkai
date: 2021-01-22 09:00:00 +0800
published: true
mermaid: true
categories: [学习笔记]
tags: [kernel, rtthread]
---

## 整体框架

![plantuml](https://www.plantuml.com/plantuml/png/ZLPRRzn457xVNp7agGLjfUG1K2Yb6w_J67RNndRJWYfPhZsRM5tRg_6aLRH4QajBqa129KeQIg5HnIK89MbKBa5Db3-pzcwU-XSOx-LaV5b4NkATx_lEcNCvCtCne2QX2swZy0QTnov6rnkcTQDumtFcvccXoRxDEOnAYeBEdw_vDhvm0RKAYFrP3JC8a3preIZe4wr2RsqfWum3iWJ6b4f9dwx8QZNVP4cHSip58gDlCyVab2ph5RbK5jLycmnFgn4dBwlIR5OQKB9WqG5eL2IDQT7WJv84eqoScvWWczmq7CS2I1GLLQxoACPDuhj0cAwKj1aUhxCzpWEiAH8F1aq785LFU2NK0gYApM21O6lUQV8K5mT0gGXb7cfODa2I9h_pxlZRYP027s1HAoK32amtNI4k9QaqYRDl8XltalJ-uByn3fIRlcCZGWrdmZ8itwF4Rvmv-rukJ8df1NLC69xn3bd_dni8_3fDRQ9V9eDWqsOUCfXFNECMSIXEklTyYX7rcvEeVNJSURGjJGYT9_VwjhZzyKLl9MeDssELvlBYU7GWqgHFnPnbfNH978M9jN8cW_EtOW-zNZCSpw6P6FiGX9Z583NfyPifLTB3CuIacYwgqoL1JCwKE9ipK6mLGOECGg1oC1A04dggWzocKWi325Xo-YufaWpGNDFnETtbage3jc0Ioh1K8v3us4H-7IASdCpww3nO3h-uVxg6FRkdxlqmhxCScHRbfehPuX8r8HZwOXENSHr9Na1Dpy80ia8OCK6Z9iL3LlmZIwdwDZ3YxsIzWOLTuqgl8-BbT5Vq66P0CT7ZqNGTQkXNHPwwb1VJe3AjhCiOaTIFPqpFRc2IvnDeGu__ILAnXTd4PNUqb6pIgb8Hgs9jq8-9p1lZBL2a8KsUrfCeX0T2SCXVLzg8wvJrdY3NT5Mkd2R79CHSZ96udGQsE8agNcBheZfA27Wi1-mjWkUSk723eo0dAMD2LPEqeY2hubXYazedcYu97xLo3y7EorUTLy_2tIVHux_2xxOvMMrM4l8rxOETQ6CdMlyrN4bfD64gNw8jiisxIEXV66YguLitq32cu9ftfh-FWSszU-7E9hDybZDTLIxdcsQZoTZjun-YrPz0oP_aeuJHdxkTk_zqZnzsTX-3C3UnokMY8gjwCgrn_SIhkg5TaNHX1bma7LttAVNT-80PI_B7cF_Lv-7QLdZuDOiWsZg87jm-UNgRtKNjWzNsmPVHndAuiXojFNzz-DKrhtzNHVlBdSEDplT_HEi_Hz-ijO-UmhvP_DszEoU_RqRVhYJYPBuJhJ79Yk2wleUgZaNymGtEXXTfVftUCWb6aaSngPiMZayYppQ9VIv-VC5yeMBn0jVvXTDFL6pWEcLekicJuf4mEl_PkNC8kAoskpzsrbzaO1XcOCGp30mOQ82vvn_pFpJ1uFilktSU5U0nCf8nk8A0CFG11Ex5siDvmIIAqMXpBtpuIxYwrJqwElbjFrpTVdtuh51If0mVZ7AFwD6aFjvFBBEMMf-0S8Qoxj_RuVxTxelFMKDzKBY8FNl1RVmB)

```plantuml
@startuml
!theme black-knight
package APP <<Node>> {
    class OBJECT2{

    }
    class OBJECT1{

    }
}
package PLATFLORM <<Node>> {
    class API{

    }
    class PLAT_OBJECT{

    }
}
package BOOTLOADER <<Node>> {
    class BOOT_OBJECT{

    } 
}
package DRIVER <<Node>> {
    struct DRIVER_LIST{
        IIC_Driver drv_iic
        EEPROM_Driver drv_eeprom
        FLASH_Driver drv_flash
        SPI_Driver drv_spi
        RTC_Driver drv_rtc
        Measurechip_Driver drv_mes
        LCD_Driver drv_lcd
        ISO7816_Driver drv_iso
        ESAM_Driver drv_esam
    }
    class IIC_Driver{
        IIC_DEV* dev_iic=dev_iic_1
        void rt_i2c_control();
        void rt_i2c_transfer();
    }
    class EEPROM_Driver{
        IIC_DEV* dev_iic=dev_iic_soft1
        void eeprom_read();
        void eeporm_write();
    }
    note top: 使用I2C的eeprom
    class FLASH_Driver{
        SPI_DEV* dev_spi_1
        int FLASH_SIZE
        int FLASH_PAGE_SIZE
        int FLASH_END
        void rt_hw_spiflash_init();
        void flash_write();
        void flash_read();
    }
}
package HAL <<Node>> {
    package INTERFACE{
    struct DEV_LIST{
        IIC_DEV dev_iic_1
        IIC_DEV dev_iic_soft1
        RTC_DEV dev_rtc_1
        SPI_DEV dev_spi_1
        FLASH_DEV dev_flash
        GPIO_DEV dev_gpio_1
        UART_DEV dev_uart_1
    }
    note right of DEV_LIST::dev_flash
        片内flash
    end note
    abstract class IIC_DEV{
        I2C_TypeDef Instance
        HAL_I2C_StateTypeDef State
        HAL_I2C_ModeTypeDef Mode
        void HAL_I2C_Mem_Write(void);
        void I2C_MasterTransmit_TXE(void);
    }
    abstract class SPI_DEV{
        void HAL_SPI_IRQHandler(void);
        void HAL_SPI_Transmit(void);
        void HAL_SPI_Receive(void);
    }
    }
    package IMPLEMENT{
    class IIC_DEV_1{
    }
    class IIC_DEV_SOFT{
    }
    class SPI_DEV_1{
    }
    }

}
package BSP <<Node>> {
    class IO_CONTROL{
        array IO_LIST
    }

    class REGISTER_CONTROL{
        array REGISTER_LIST
        +register_init()
    }
    package "CMSIS-CORE" {
    class SYSTICK{
    }
    note top: 系统定时器
    class NVIC{
    }
    note top: 中断控制器
    class SCB{
    }
    note top: System Control Block registers\n(系统控制寄存器)
    class MPU{
    }
    note top: 内存保护寄存器
    class FPU{
    }
    note top: 浮点运算寄存器
    }
    package "CPU-PORT" {
    class CONTEXT_SWITCH{
    }
    }
    note bottom of "CONTEXT_SWITCH": 抢占式内核所需的上下文切换，\n使用汇编直接操作寄存器保证高效
    note top of "CMSIS-CORE": Common Microcontroller Software Interface Standard. 
}
IIC_DEV_1 --> IO_CONTROL
IO_CONTROL -left-> REGISTER_CONTROL
IIC_DEV_1 --> REGISTER_CONTROL
IIC_DEV <|.. IIC_DEV_1: 实现
IIC_DEV <|.. IIC_DEV_SOFT: 实现
SPI_DEV <|.. SPI_DEV_1: 实现
IIC_Driver --> IIC_DEV: 关联
EEPROM_Driver --> IIC_DEV: 关联
FLASH_Driver --> SPI_DEV: 关联
BOOT_OBJECT --> FLASH_Driver: BOOT是否加载驱动？
API --> FLASH_Driver: 关联
PLAT_OBJECT --> FLASH_Driver: 关联
OBJECT1 --> API: 关联
OBJECT2 --> IIC_Driver: 跨层调用?
@enduml
```
