#include <windows.h>
int main() {
	ShellExecute(0, "runas", "Python\\pythonw.exe", "PyPigPlayer.pyz", 0, 1);
	return 0;
}
