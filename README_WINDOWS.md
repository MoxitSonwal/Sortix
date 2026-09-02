# Sortix on Windows — PowerShell installation

Sortix runs locally on Windows using Python's standard library. It does not require Node.js, a database, or third-party Python packages.

## 1. Install Python

1. Download Python 3.10 or newer from [python.org/downloads/windows](https://www.python.org/downloads/windows/).
2. Run the installer.
3. On the first installer screen, enable **Add python.exe to PATH**.
4. Finish the installation.

Close and reopen PowerShell after installing Python.

Verify the installation:

```powershell
py --version
```

You should see Python 3.10 or newer.

## 2. Extract the Sortix ZIP

In File Explorer, right-click `Sortix.zip` and choose **Extract All**.

Or extract it from PowerShell:

```powershell
Expand-Archive -Path .\Sortix.zip -DestinationPath .\Sortix
```

If the extracted archive contains a `sortix` folder, enter that folder:

```powershell
Set-Location .\Sortix\sortix
```

If you extracted the contents directly into `Sortix`, use:

```powershell
Set-Location .\Sortix
```

Confirm that `app.py` is present:

```powershell
Get-ChildItem .\app.py
```

## 3. Start Sortix

Run:

```powershell
py .\app.py
```

You should see:

```text
Sortix is running at http://127.0.0.1:8765
```

Open this address in your browser:

<http://127.0.0.1:8765>

Sortix binds to `127.0.0.1`, so the application is available only on your computer by default.

## 4. Scan a folder

1. Enter a Windows folder path in **Selected folder**.
2. Examples:

   ```text
   C:\Users\YourName\Downloads
   C:\Users\YourName\Desktop
   C:\Users\YourName\Documents
   ```

   You can also use the PowerShell home shortcut:

   ```text
   ~\Downloads
   ```

3. Select **Scan folder**.
4. Review the file landscape and suggested sorting plan.
5. Use **Review sorting plan** before approving any file moves.

Sortix never deletes files and does not overwrite an existing destination. If a name already exists, it creates a collision-safe name such as `photo (1).jpg`.

## 5. Use another port

If port `8765` is already in use:

```powershell
py .\app.py --port 9000
```

Then open:

<http://127.0.0.1:9000>

## 6. Stop Sortix

Return to the PowerShell window running Sortix and press:

```text
Ctrl+C
```

## 7. Run the tests

From the folder containing `app.py`:

```powershell
py -m unittest discover -s tests -v
```

The tests use temporary directories and do not touch your personal files.

You can also verify the Python source:

```powershell
py -m compileall backend app.py
```

## Troubleshooting

### `py` is not recognized

Python was not added to PATH. Re-run the Python installer and enable **Add python.exe to PATH**, then reopen PowerShell. You can also try:

```powershell
python --version
```

### The browser cannot connect

Check that the PowerShell window running Sortix is still open. If port `8765` is busy, start Sortix on another port using `--port 9000`.

### Access is denied while scanning

Choose a folder your Windows account can access, such as your own `Downloads` or `Documents` folder. Avoid protected Windows system directories.

### A file was not moved

Sortix can skip files that have disappeared, are protected, are outside the selected root, or already have their intended destination. Review the skipped items shown in the preview instead of retrying blindly.

## Uninstall

Stop the Sortix process and delete the extracted Sortix folder. Sortix stores operation history in:

```text
%USERPROFILE%\.sortix\history.json
```

Delete that `.sortix` folder separately if you also want to remove local Sortix history.