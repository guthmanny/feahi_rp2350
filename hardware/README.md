# SP-1 硬件

硬件按 **profile** 组织；与 MCU/SDK 无关的网表与规格放在各 profile 下。

| Profile | 说明 |
|---------|------|
| [**sp-1/**](profiles/sp-1/) | **量产单板** KiCad 主工程（RP2350 + C6 + Codec + UI） |
| [**b-c6/**](profiles/b-c6/) | 模块化 **CBI-40** 参考（Core / Periph 模板、MIDI 光耦电路、datasheets） |

连接器机械代号 **FEAHI-CBI-40** 仅用于 b-c6 模块化方案。

产品级说明：[docs/hardware.md](../docs/hardware.md)
