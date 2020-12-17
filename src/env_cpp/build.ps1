if ($null -eq (Get-Command "protoc.exe" -ErrorAction SilentlyContinue))
{
    Write-Host "Please install the Protobuf compiler first"
}

protoc -I protobuf protobuf/message.proto --cpp_out=env

mkdir .\build -ErrorAction SilentlyContinue
Push-Location .\build
cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_TOOLCHAIN_FILE=$VCPKG_ROOT/scripts/buildsystems/vcpkg.cmake ..
Pop-Location

Write-Host "Start Visual Studio developer command prompt and use msbuild to build the projects"
Write-Host "msbuild ALL_BUILD.vcxproj /p:Configuration=[Debug|Release]"