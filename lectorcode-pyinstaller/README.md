### Step 1: Install PyInstaller

If you haven't already installed PyInstaller, you can do so using pip. Open your terminal or command prompt and run:

```bash
pip install pyinstaller
```

### Step 2: Create a New Directory for the Project

Create a new directory for your PyInstaller project. This will help keep your files organized.

```bash
mkdir LectorCodeExecutable
cd LectorCodeExecutable
```

### Step 3: Copy Your Application Files

Copy the necessary files from your existing LectorCode application into the new directory. You will need at least the `main.py` file and any other modules or resources your application depends on.

For example, if your `main.py` is located at `c:\Users\juanc\Documents\NUVU\LectorCode\main.py`, you can copy it like this:

```bash
copy c:\Users\juanc\Documents\NUVU\LectorCode\main.py .
```

Also, copy the `src` directory if it contains the `MainWindow` class and any other necessary files.

### Step 4: Create a PyInstaller Spec File (Optional)

You can create a `.spec` file to customize the build process. However, for a simple application, you can directly use PyInstaller without a spec file.

### Step 5: Generate the Executable

Run PyInstaller with your `main.py` file. You can use the following command:

```bash
pyinstaller --onefile --windowed main.py
```

- `--onefile`: This option tells PyInstaller to bundle everything into a single executable file.
- `--windowed`: This option prevents a console window from appearing when you run the GUI application.

### Step 6: Locate the Executable

After running the PyInstaller command, you will see a new directory called `dist` created in your project folder. Inside the `dist` directory, you will find the executable file named `main.exe` (or just `main` on non-Windows systems).

### Step 7: Test the Executable

Navigate to the `dist` directory and run the executable to ensure that it works as expected:

```bash
cd dist
./main.exe  # On Windows
# or
./main  # On Linux/Mac
```

### Step 8: Distribute Your Application

You can now distribute the executable file found in the `dist` directory. Make sure to include any necessary resources or dependencies that your application might need.

### Additional Notes

- If your application has additional dependencies (like images, data files, etc.), you may need to specify them in the PyInstaller command or in the spec file.
- If you encounter any issues, you can check the `build` directory for logs and troubleshoot accordingly.

By following these steps, you should be able to create an executable file for your LectorCode application using PyInstaller.