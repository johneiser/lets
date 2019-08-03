FROM mcr.microsoft.com/powershell

RUN apt-get update \
    && apt-get install -qy git \
    && git clone https://github.com/danielbohannon/Invoke-Obfuscation \
    && for i in $(ls /opt/microsoft/powershell/);do echo "Import-Module /Invoke-Obfuscation/Invoke-Obfuscation.psd1" >> /opt/microsoft/powershell/$i/profile.ps1;done
