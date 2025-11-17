#include "MainWindow.h"
#include "SettingsDialog.h"
#include <QApplication>
#include <QMessageBox>
#include <QDateTime>
#include <QDir>
#include <QStandardPaths>
#include <QStyleFactory>
#include <QFile>           
#include <QTextCursor>     
#include <QIcon>           
#include <QGroupBox>       
#include <QVBoxLayout>     // ADD THIS
#include <QHBoxLayout>     // ADD THIS
#include <QLabel>          // ADD THIS
#include <QPushButton>     // ADD THIS
#include <QProgressBar>    // ADD THIS
#include <QTextEdit>       // ADD THIS
#include <QComboBox>       // ADD THIS
#include <QSystemTrayIcon> // ADD THIS
#include <QMenu>           // ADD THIS
#include <QAction>         // ADD THIS
#include <QCloseEvent>     // ADD THIS
#include <QFileDialog>
#include <QMessageBox>

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent), 
      isRunning(false),
      pythonProcess(nullptr),
      settings(nullptr),
      trayIcon(nullptr),
      trayMenu(nullptr),
      startButton(nullptr),
      stopButton(nullptr),
      settingsButton(nullptr),
      outputText(nullptr),
      statusLabel(nullptr),
      languageLabel(nullptr),
      progressBar(nullptr),
      sourceLanguageCombo(nullptr),
      targetLanguageCombo(nullptr),
      outputFolder(""),
      outputFolderLabel(nullptr),
      folderButton(nullptr)
{
    // Initialize QProcess first
    pythonProcess = new QProcess(this);
    pythonProcess->setProcessChannelMode(QProcess::MergedChannels);
    
    settings = new QSettings("Michael7664", "RealTimeTranslator", this);
    
    setupUI();
    setupConnections();
    setupTrayIcon();
    loadSettings();
    
    setWindowTitle("Real-Time Translator");
    setMinimumSize(900, 700);
    
    // Add application icon (simple fix for tray icon warning)
    setWindowIcon(QIcon());
}

void MainWindow::setupUI()
{
    QWidget *centralWidget = new QWidget(this);
    setCentralWidget(centralWidget);
    
    QVBoxLayout *mainLayout = new QVBoxLayout(centralWidget);
    
    // Header
    QLabel *titleLabel = new QLabel("Real-Time Audio Translator");
    titleLabel->setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; padding: 10px;");
    mainLayout->addWidget(titleLabel);
    
    // === ADD OUTPUT FOLDER SELECTION ===
    QGroupBox *outputFolderGroup = new QGroupBox("Output Location");
    QHBoxLayout *folderLayout = new QHBoxLayout(outputFolderGroup);
    
    QLabel *folderLabel = new QLabel("Save translations to:");
    outputFolderLabel = new QLabel("Not selected (will use default location)");
    outputFolderLabel->setStyleSheet("color: #7f8c8d; font-style: italic;");
    outputFolderLabel->setWordWrap(true);
    
    folderButton = new QPushButton("📁 Choose Folder");
    folderButton->setStyleSheet("QPushButton { background-color: #95a5a6; color: white; padding: 5px 10px; border-radius: 3px; }");
    
    folderLayout->addWidget(folderLabel);
    folderLayout->addWidget(outputFolderLabel, 1); // Give it stretch
    folderLayout->addWidget(folderButton);
    
    mainLayout->addWidget(outputFolderGroup);
    // === END OUTPUT FOLDER SELECTION ===
    
    // Language Selection Panel
    QGroupBox *languageGroup = new QGroupBox("Language Settings");
    QHBoxLayout *languageLayout = new QHBoxLayout(languageGroup);
    
    QLabel *sourceLabel = new QLabel("Translate from:");
    sourceLanguageCombo = new QComboBox();
    sourceLanguageCombo->addItem("Italian", "it");
    sourceLanguageCombo->addItem("Spanish", "es");
    sourceLanguageCombo->addItem("French", "fr");
    sourceLanguageCombo->addItem("German", "de");
    sourceLanguageCombo->addItem("Chinese", "zh");
    sourceLanguageCombo->addItem("Japanese", "ja");
    sourceLanguageCombo->addItem("Korean", "ko");
    sourceLanguageCombo->addItem("Russian", "ru");
    sourceLanguageCombo->addItem("Portuguese", "pt");
    sourceLanguageCombo->addItem("Arabic", "ar");
    sourceLanguageCombo->addItem("Hindi", "hi");
    
    QLabel *targetLabel = new QLabel("to:");
    targetLanguageCombo = new QComboBox();
    targetLanguageCombo->addItem("English", "en");
    targetLanguageCombo->addItem("Spanish", "es");
    targetLanguageCombo->addItem("French", "fr");
    targetLanguageCombo->addItem("German", "de");
    targetLanguageCombo->addItem("Italian", "it");
    targetLanguageCombo->addItem("Chinese", "zh");
    targetLanguageCombo->addItem("Japanese", "ja");
    targetLanguageCombo->addItem("Korean", "ko");
    targetLanguageCombo->addItem("Russian", "ru");
    
    languageLayout->addWidget(sourceLabel);
    languageLayout->addWidget(sourceLanguageCombo);
    languageLayout->addSpacing(20);
    languageLayout->addWidget(targetLabel);
    languageLayout->addWidget(targetLanguageCombo);
    languageLayout->addStretch();
    
    // Control Panel
    QGroupBox *controlGroup = new QGroupBox("Translation Controls");
    QHBoxLayout *controlLayout = new QHBoxLayout(controlGroup);
    
    startButton = new QPushButton("🎤 Start Translation");
    stopButton = new QPushButton("⏹ Stop Translation");
    settingsButton = new QPushButton("⚙ Settings");
    
    startButton->setStyleSheet("QPushButton { background-color: #27ae60; color: white; font-weight: bold; padding: 10px 20px; border-radius: 5px; }");
    stopButton->setStyleSheet("QPushButton { background-color: #e74c3c; color: white; font-weight: bold; padding: 10px 20px; border-radius: 5px; }");
    settingsButton->setStyleSheet("QPushButton { background-color: #3498db; color: white; font-weight: bold; padding: 10px 20px; border-radius: 5px; }");
    
    stopButton->setEnabled(false);
    
    controlLayout->addWidget(startButton);
    controlLayout->addWidget(stopButton);
    controlLayout->addWidget(settingsButton);
    controlLayout->addStretch();
    
    // Status Panel
    QGroupBox *statusGroup = new QGroupBox("Status");
    QVBoxLayout *statusLayout = new QVBoxLayout(statusGroup);
    
    statusLabel = new QLabel("Ready to start translation");
    statusLabel->setStyleSheet("font-weight: bold; padding: 5px;");
    
    languageLabel = new QLabel();
    languageLabel->setStyleSheet("color: #7f8c8d; padding: 5px;");
    
    progressBar = new QProgressBar();
    progressBar->setRange(0, 0); // Indeterminate progress
    progressBar->setVisible(false);
    progressBar->setStyleSheet("QProgressBar { height: 10px; }");
    
    statusLayout->addWidget(statusLabel);
    statusLayout->addWidget(languageLabel);
    statusLayout->addWidget(progressBar);
    
    // Output Panel
    QGroupBox *outputGroup = new QGroupBox("Live Translations");
    QVBoxLayout *outputLayout = new QVBoxLayout(outputGroup);
    
    outputText = new QTextEdit();
    outputText->setReadOnly(true);
    outputText->setPlaceholderText("Translations will appear here in real-time...\n\nInstructions:\n1. Select source and target languages\n2. Click 'Start Translation'\n3. Ensure audio is playing through speakers\n4. Translations will appear automatically");
    outputText->setStyleSheet("QTextEdit { font-family: 'Courier New'; font-size: 12px; }");
    
    outputLayout->addWidget(outputText);
    
    // Assemble main layout
    mainLayout->addWidget(languageGroup);
    mainLayout->addWidget(controlGroup);
    mainLayout->addWidget(statusGroup);
    mainLayout->addWidget(outputGroup);
}

void MainWindow::setupConnections()
{
    connect(startButton, &QPushButton::clicked, this, &MainWindow::startTranslation);
    connect(stopButton, &QPushButton::clicked, this, &MainWindow::stopTranslation);
    connect(settingsButton, &QPushButton::clicked, this, &MainWindow::showSettings);
    connect(folderButton, &QPushButton::clicked, this, &MainWindow::selectOutputFolder);
    connect(pythonProcess, &QProcess::readyReadStandardOutput, this, &MainWindow::updateOutput);
    connect(pythonProcess, &QProcess::finished, this, &MainWindow::processFinished);
    connect(pythonProcess, &QProcess::errorOccurred, this, &MainWindow::processErrorOccurred);
    
    // Update language display when selection changes
    connect(sourceLanguageCombo, QOverload<int>::of(&QComboBox::currentIndexChanged), this, [this]() {
        updateLanguageDisplay();
    });
    connect(targetLanguageCombo, QOverload<int>::of(&QComboBox::currentIndexChanged), this, [this]() {
        updateLanguageDisplay();
    });
}

void MainWindow::setupTrayIcon()
{
    trayIcon = new QSystemTrayIcon(this);
    trayIcon->setIcon(QApplication::windowIcon());
    
    trayMenu = new QMenu(this);
    QAction *showAction = new QAction("Show", this);
    QAction *hideAction = new QAction("Hide", this);
    QAction *quitAction = new QAction("Quit", this);
    
    connect(showAction, &QAction::triggered, this, &MainWindow::showWindow);
    connect(hideAction, &QAction::triggered, this, &MainWindow::hideWindow);
    connect(quitAction, &QAction::triggered, qApp, &QApplication::quit);
    
    trayMenu->addAction(showAction);
    trayMenu->addAction(hideAction);
    trayMenu->addSeparator();
    trayMenu->addAction(quitAction);
    
    trayIcon->setContextMenu(trayMenu);
    trayIcon->show();
    
    connect(trayIcon, &QSystemTrayIcon::activated, this, &MainWindow::trayIconActivated);
}

void MainWindow::loadSettings()
{
    settings->beginGroup("Language");
    QString sourceLang = settings->value("source", "it").toString();
    QString targetLang = settings->value("target", "en").toString();
    settings->endGroup();
    
    // Load output folder
    settings->beginGroup("Output");
    outputFolder = settings->value("folder", "").toString();
    settings->endGroup();
    
    // Set combo boxes
    int sourceIndex = sourceLanguageCombo->findData(sourceLang);
    if (sourceIndex >= 0) sourceLanguageCombo->setCurrentIndex(sourceIndex);
    
    int targetIndex = targetLanguageCombo->findData(targetLang);
    if (targetIndex >= 0) targetLanguageCombo->setCurrentIndex(targetIndex);
    
    updateLanguageDisplay();
    updateOutputFolderDisplay();
}

void MainWindow::saveSettings()
{
    settings->beginGroup("Language");
    settings->setValue("source", sourceLanguageCombo->currentData());
    settings->setValue("target", targetLanguageCombo->currentData());
    settings->endGroup();
    
    // Save output folder
    settings->beginGroup("Output");
    settings->setValue("folder", outputFolder);
    settings->endGroup();
}

void MainWindow::updateLanguageDisplay()
{
    QString sourceLang = sourceLanguageCombo->currentText();
    QString targetLang = targetLanguageCombo->currentText();
    languageLabel->setText(QString("Translating: %1 → %2").arg(sourceLang, targetLang));
}

void MainWindow::selectOutputFolder()
{
    QString folder = QFileDialog::getExistingDirectory(
        this,
        "Select Folder for Translation Files",
        QDir::homePath(),
        QFileDialog::ShowDirsOnly | QFileDialog::DontResolveSymlinks
    );
    
    if (!folder.isEmpty()) {
        outputFolder = folder;
        updateOutputFolderDisplay();
        saveSettings();
        
        outputText->append("<span style='color: green;'>✓ Output folder set to: " + outputFolder + "</span>");
    }
}

void MainWindow::updateOutputFolderDisplay()
{
    if (outputFolder.isEmpty()) {
        outputFolderLabel->setText("Not selected (will use default location)");
        outputFolderLabel->setStyleSheet("color: #7f8c8d; font-style: italic;");
    } else {
        // Show abbreviated path if too long
        QString displayPath = outputFolder;
        if (displayPath.length() > 50) {
            displayPath = "..." + displayPath.right(47);
        }
        outputFolderLabel->setText(displayPath);
        outputFolderLabel->setStyleSheet("color: #27ae60; font-weight: bold;");
        outputFolderLabel->setToolTip(outputFolder); // Show full path on hover
    }
}

void MainWindow::startTranslation()
{
    if (isRunning) return;
    
    outputText->clear();
    outputText->append("<span style='color: green;'>[DEBUG] Starting translation process...</span>");
    
    // Use the GUI backend
    QString pythonBridge = QApplication::applicationDirPath() + "/gui_backend.py";
    
    outputText->append("Looking for: " + pythonBridge);
    outputText->append("Application dir: " + QApplication::applicationDirPath());
    
    if (!QFile::exists(pythonBridge)) {
        outputText->append("<span style='color: red;'>ERROR: GUI bridge not found at: " + pythonBridge + "</span>");
        return;
    }
    
    // Get selected languages
    QString sourceLang = sourceLanguageCombo->currentData().toString();
    QString targetLang = targetLanguageCombo->currentData().toString();
    
    outputText->append("Starting translation: " + sourceLang + " → " + targetLang);
    
    // Show output folder info
    if (outputFolder.isEmpty()) {
        outputText->append("<span style='color: orange;'>Using default output location</span>");
    } else {
        outputText->append("<span style='color: green;'>Output folder: " + outputFolder + "</span>");
    }
    
    statusLabel->setText("Starting translation...");
    progressBar->setVisible(true);
    
    // Start Python process with language arguments AND output folder
    QStringList arguments;
    arguments << pythonBridge << sourceLang << targetLang;
    
    // Add output folder as argument if specified
    if (!outputFolder.isEmpty()) {
        arguments << outputFolder;
    }
    
    // Set working directory to build directory
    pythonProcess->setWorkingDirectory(QApplication::applicationDirPath());
    
    outputText->append("Starting Python process: python " + arguments.join(" "));
    
    pythonProcess->start("python", arguments);
    
    if (pythonProcess->waitForStarted(5000)) {
        isRunning = true;
        startButton->setEnabled(false);
        stopButton->setEnabled(true);
        settingsButton->setEnabled(false);
        statusLabel->setText("Translation running...");
        
        outputText->append("<span style='color: green;'>✓ Python backend started successfully</span>");
    } else {
        QString error = "Failed to start Python backend!\n";
        error += "Process error: " + QString::number(pythonProcess->error()) + "\n";
        error += "Error: " + pythonProcess->errorString();
        
        outputText->append("<span style='color: red;'>" + error + "</span>");
        QMessageBox::critical(this, "Error", error);
        statusLabel->setText("Failed to start");
        progressBar->setVisible(false);
    }
}

void MainWindow::stopTranslation()
{
    if (!isRunning) return;
    
    pythonProcess->terminate();
    if (!pythonProcess->waitForFinished(5000)) {
        pythonProcess->kill();
    }
    
    isRunning = false;
    startButton->setEnabled(true);
    stopButton->setEnabled(false);
    settingsButton->setEnabled(true);
    progressBar->setVisible(false);
    statusLabel->setText("Translation stopped");
    
    outputText->append("[" + QDateTime::currentDateTime().toString("hh:mm:ss") + "] Translation stopped");
}

void MainWindow::showSettings()
{
    SettingsDialog dialog(this);
    dialog.exec();
}

void MainWindow::updateOutput()
{
    if (!pythonProcess) {
        outputText->append("<span style='color: red;'>[ERROR] pythonProcess is null!</span>");
        return;
    }
    
    QByteArray output = pythonProcess->readAllStandardOutput();
    QString outputTextStr = QString::fromLocal8Bit(output);
    
    // Debug: show raw output
    if (!outputTextStr.isEmpty()) {
        outputText->append("<span style='color: gray;'>[RAW] " + outputTextStr + "</span>");
    }
    
    QStringList lines = outputTextStr.split('\n');
    for (const QString &line : lines) {
        if (!line.trimmed().isEmpty()) {
            // Parse different message types for color coding and display
            if (line.contains("🚀") || line.contains("Starting") || line.contains("initialized")) {
                outputText->append("<span style='color: green;'>[" + QDateTime::currentDateTime().toString("hh:mm:ss") + "] " + line + "</span>");
            } 
            else if (line.contains("🔊 RECOGNIZED_ITALIAN:")) {
                QString recognized = line.mid(line.indexOf("RECOGNIZED_ITALIAN:") + 20);
                outputText->append("<span style='color: blue; font-weight: bold;'>[" + QDateTime::currentDateTime().toString("hh:mm:ss") + "] 🔊 Italian: " + recognized + "</span>");
            }
            else if (line.contains("🌐 TRANSLATED_ENGLISH:")) {
                QString translated = line.mid(line.indexOf("TRANSLATED_ENGLISH:") + 20);
                outputText->append("<span style='color: green; font-weight: bold;'>[" + QDateTime::currentDateTime().toString("hh:mm:ss") + "] 🌐 English: " + translated + "</span>");
                
                // Also update the status with the latest translation
                statusLabel->setText("Last: " + translated);
            }
            else if (line.contains("❌") || line.contains("ERROR")) {
                outputText->append("<span style='color: red;'>[" + QDateTime::currentDateTime().toString("hh:mm:ss") + "] " + line + "</span>");
            }
            else if (line.contains("🔇") || line.contains("No speech")) {
                outputText->append("<span style='color: orange;'>[" + QDateTime::currentDateTime().toString("hh:mm:ss") + "] " + line + "</span>");
            }
            else if (line.contains("📊") || line.contains("Audio buffer")) {
                // Show audio level in status
                statusLabel->setText(line);
            }
            else if (line.contains("🔍") || line.contains("Attempting")) {
                outputText->append("<span style='color: purple;'>[" + QDateTime::currentDateTime().toString("hh:mm:ss") + "] " + line + "</span>");
            }
            else if (line.contains("🔄") || line.contains("Translating")) {
                outputText->append("<span style='color: teal;'>[" + QDateTime::currentDateTime().toString("hh:mm:ss") + "] " + line + "</span>");
            }
            else if (line.contains("⚠️") || line.contains("No audio")) {
                outputText->append("<span style='color: orange; font-weight: bold;'>[" + QDateTime::currentDateTime().toString("hh:mm:ss") + "] " + line + "</span>");
            }
            else {
                outputText->append("[" + QDateTime::currentDateTime().toString("hh:mm:ss") + "] " + line);
            }
            
            // Auto-scroll to bottom
            QTextCursor cursor = outputText->textCursor();
            cursor.movePosition(QTextCursor::End);
            outputText->setTextCursor(cursor);
            
            // Ensure the text edit updates
            outputText->repaint();
            
            // Force GUI update
            QApplication::processEvents();
        }
    }
}

void MainWindow::processFinished(int exitCode, QProcess::ExitStatus exitStatus)
{
    isRunning = false;
    startButton->setEnabled(true);
    stopButton->setEnabled(false);
    settingsButton->setEnabled(true);
    progressBar->setVisible(false);
    
    if (exitStatus == QProcess::NormalExit) {
        statusLabel->setText("Translation completed successfully");
        outputText->append("[" + QDateTime::currentDateTime().toString("hh:mm:ss") + "] Translation completed");
    } else {
        statusLabel->setText("Translation process ended");
        outputText->append("[" + QDateTime::currentDateTime().toString("hh:mm:ss") + "] Process ended with code: " + QString::number(exitCode));
    }
}

void MainWindow::processErrorOccurred(QProcess::ProcessError error)
{
    QString errorText;
    switch (error) {
        case QProcess::FailedToStart: errorText = "Failed to start"; break;
        case QProcess::Crashed: errorText = "Crashed"; break;
        case QProcess::Timedout: errorText = "Timed out"; break;
        case QProcess::WriteError: errorText = "Write error"; break;
        case QProcess::ReadError: errorText = "Read error"; break;
        default: errorText = "Unknown error"; break;
    }
    
    statusLabel->setText("Process error: " + errorText);
    outputText->append("[" + QDateTime::currentDateTime().toString("hh:mm:ss") + "] Error: " + errorText);
}

void MainWindow::trayIconActivated(QSystemTrayIcon::ActivationReason reason)
{
    if (reason == QSystemTrayIcon::DoubleClick) {
        if (isVisible()) {
            hideWindow();
        } else {
            showWindow();
        }
    }
}

void MainWindow::showWindow()
{
    show();
    raise();
    activateWindow();
}

void MainWindow::hideWindow()
{
    hide();
}

void MainWindow::closeEvent(QCloseEvent *event)
{
    if (isRunning) {
        QMessageBox::StandardButton reply = QMessageBox::question(this, "Confirm Exit", 
            "Translation is still running. Are you sure you want to exit?",
            QMessageBox::Yes | QMessageBox::No);
        
        if (reply == QMessageBox::No) {
            event->ignore();
            return;
        }
        
        stopTranslation();
    }
    
    hide();
    event->ignore(); // Keep running in tray
}

MainWindow::~MainWindow()
{
    if (isRunning) {
        stopTranslation();
    }
}