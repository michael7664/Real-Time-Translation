#include "SettingsDialog.h"
#include <QVBoxLayout>
#include <QHBoxLayout>
#include <QGroupBox>
#include <QLabel>
#include <QPushButton>
#include <QDialogButtonBox>
#include <QCheckBox>
#include <QSpinBox>
#include <QComboBox>
#include <QSettings>

SettingsDialog::SettingsDialog(QWidget *parent)
    : QDialog(parent)
{
    setupUI();
    loadSettings();
    
    setWindowTitle("Settings");
    setFixedSize(400, 300);
}

void SettingsDialog::setupUI()
{
    QVBoxLayout *mainLayout = new QVBoxLayout(this);
    
    // General Settings
    QGroupBox *generalGroup = new QGroupBox("General Settings");
    QVBoxLayout *generalLayout = new QVBoxLayout(generalGroup);
    
    QCheckBox *minimizeToTrayCheck = new QCheckBox("Minimize to system tray when closed");
    QCheckBox *autoStartCheck = new QCheckBox("Start with system (not implemented)");
    autoStartCheck->setEnabled(false);
    
    generalLayout->addWidget(minimizeToTrayCheck);
    generalLayout->addWidget(autoStartCheck);
    
    // Audio Settings
    QGroupBox *audioGroup = new QGroupBox("Audio Settings");
    QHBoxLayout *audioLayout = new QHBoxLayout(audioGroup);
    
    QLabel *timeoutLabel = new QLabel("Processing interval:");
    QSpinBox *audioTimeoutSpin = new QSpinBox();
    audioTimeoutSpin->setRange(1, 10);
    audioTimeoutSpin->setValue(3);
    audioTimeoutSpin->setSuffix(" seconds");
    
    audioLayout->addWidget(timeoutLabel);
    audioLayout->addWidget(audioTimeoutSpin);
    audioLayout->addStretch();
    
    // Buttons
    QDialogButtonBox *buttonBox = new QDialogButtonBox(QDialogButtonBox::Ok | QDialogButtonBox::Cancel);
    connect(buttonBox, &QDialogButtonBox::accepted, this, &SettingsDialog::saveSettings);
    connect(buttonBox, &QDialogButtonBox::rejected, this, &QDialog::reject);
    
    // Assemble layout
    mainLayout->addWidget(generalGroup);
    mainLayout->addWidget(audioGroup);
    mainLayout->addStretch();
    mainLayout->addWidget(buttonBox);
}

void SettingsDialog::loadSettings()
{
    QSettings settings("Michael7664", "RealTimeTranslator");
    // Load settings here
}

void SettingsDialog::saveSettings()
{
    QSettings settings("Michael7664", "RealTimeTranslator");
    // Save settings here
    accept();
}