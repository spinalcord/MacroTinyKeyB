This projects continues [MacroKeyB](https://github.com/spinalcord/MacroKeyB) which was written in rust.
MacroTinyKeyB is a Linux-exclusive tool (currently) that transforms any secondary keyboard into a powerful macro controller. By intercepting and blocking input from a secondary keyboard, MacroTinyKeyB allows you to assign custom Lua scripts to each key, creating a dedicated macro pad for productivity, gaming, or creative workflows.

| Name            | Language | Speed           | Permissions                             | Rendering Issues                  | Complexity           | Compatiblity          |
|------------------|----------|------------------|----------------------------------------|-----------------------------------|----------------------|----------------------|
| MacroTinyKeyb 👍   | Python   | Slightly slower   | Requires one-time input permission via terminal      | No rendering issues because of Qt | Low complexity       | x11/xwayland
| MacroKeyb(Deprecated)        | Rust     | Fast             | Requires full sudo rights every time   | Rendering issues due to Tauri    | Very complicated duo to Rust safe threading      | x11/wayland


![image](https://github.com/user-attachments/assets/5fa86ad9-30f9-48ee-8476-2f2e61763477)
![image](https://github.com/user-attachments/assets/5be67c80-e135-4018-bd0f-4e76e4dead37)

# Simple
In a Nutshell
- Grabb the second Keyboard
- Press a Key for instance "s"
- Open the Scripts folder (your macro key is created automatically "s.lua")
- Write lua code in it
- Fire you macro

![image](https://github.com/user-attachments/assets/eec4cf30-2f17-44c8-8fbf-809a144da81a)

# Build

Create a conda enviroment with my preset

```
conda env create -f _condaEnv.yml
```
then do `pyinstaller main.spec`

# Executable / Download

You can download the executable [here](https://github.com/spinalcord/MacroTinyKeyB/releases/tag/Rlease).
