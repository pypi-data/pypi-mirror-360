from mooch.validators import architecture, command, env_var, operating_system, python_version, virtual_env

command.check(["git", "python3", "curl"])
print("All required commands are available.")

architecture.check(["x86_64", "arm64"])
print("Architecture is supported.")

virtual_env.check()
print("Virtual environment is activated.")

python_version.check("3.8")
print("Python version is compatible.")

operating_system.check(["Linux", "Darwin", "Windows"])
print("Operating system is supported.")

env_var.check(["HOME"])
print("Environment variable HOME is set.")
