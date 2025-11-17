#include "MainWindow.h"
#include <QApplication>

int main(int argc, char *argv[])
{
    QApplication app(argc, argv);
    
    // Set application properties
    app.setApplicationName("Real-Time Translator");
    app.setApplicationVersion("1.0");
    app.setOrganizationName("Michael7664");
    app.setApplicationDisplayName("Real-Time Audio Translator");
    
    MainWindow window;
    window.show();
    
    return app.exec();
}