#ifndef MAINWINDOW_H
#define MAINWINDOW_H

#include <QMainWindow>
#include <QPushButton>
#include <QTextEdit>
#include <QLabel>
#include <QProgressBar>
#include <QProcess>
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QGroupBox>
#include <QComboBox>
#include <QSettings>
#include <QSystemTrayIcon>
#include <QMenu>
#include <QAction>
#include <QCloseEvent>

// Include SettingsDialog directly instead of forward declaration
#include "SettingsDialog.h"

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    MainWindow(QWidget *parent = nullptr);
    ~MainWindow();

protected:
    void closeEvent(QCloseEvent *event) override;

private slots:
    void startTranslation();
    void stopTranslation();
    void showSettings();
    void updateOutput();
    void processFinished(int exitCode, QProcess::ExitStatus exitStatus);
    void processErrorOccurred(QProcess::ProcessError error);
    void trayIconActivated(QSystemTrayIcon::ActivationReason reason);
    void showWindow();
    void hideWindow();
    void selectOutputFolder();
    void updateOutputFolderDisplay();

private:
    void setupUI();
    void setupConnections();
    void setupTrayIcon();
    void loadSettings();
    void saveSettings();
    void updateLanguageDisplay();
    
    // UI Components
    QPushButton *startButton;
    QPushButton *stopButton;
    QPushButton *settingsButton;
    QTextEdit *outputText;
    QLabel *statusLabel;
    QLabel *languageLabel;
    QProgressBar *progressBar;
    QComboBox *sourceLanguageCombo;
    QComboBox *targetLanguageCombo;
    
    // Output Folder Components
    QString outputFolder;
    QLabel *outputFolderLabel;
    QPushButton *folderButton;
    
    // Backend
    QProcess *pythonProcess;
    bool isRunning;
    
    // Settings
    QSettings *settings;
    
    // System Tray
    QSystemTrayIcon *trayIcon;
    QMenu *trayMenu;
};

#endif // MAINWINDOW_H