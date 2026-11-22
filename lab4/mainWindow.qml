import QtQuick 2.0
import QtQuick.Window 2.3
import QtQuick.Controls 2.0
import QtQuick.Layouts 1.3

import "."

Window {
    id: root
    visible: true
    width: 1100
    height: 800
    title: "Лабораторная работа #4 Буторина 6231"
    color: "#1e1e1e"

    property int autosaveInterval: 5000
    property bool hasDrawn: false
    property bool eraserMode: false
    property bool autosaveOn: true

    property bool cursorVisible: false
    property point cursorPos: Qt.point(-100, -100)

    property string toastText: ""
    property bool toastVisible: false

    function showToast(msg) {
        toastText = msg
        toastVisible = true
        toastTimer.restart()
    }

    function saveNow() {
        if (!hasDrawn) {
            showToast("Полотно пустое! Нарисуйте что-нибудь")
            return
        }
        var dataUrl = canvas.toDataURL()
        if (dataUrl && dataUrl.length > 0) {
            _backend.saveCanvas(dataUrl)
            showToast("Сохранено")
        }
    }

    function captureCanvas() {
        if (!hasDrawn) return
        saveNow()
    }

    function clearCanvas() {
        canvas.resetCanvas()
        hasDrawn = false
        showToast("Очищено")
    }

    Timer {
        id: autosaveTimer
        interval: root.autosaveInterval
        running: root.autosaveOn
        repeat: true
        onTriggered: root.captureCanvas()
    }

    Timer {
        id: toastTimer
        interval: 2000
        onTriggered: toastVisible = false
    }

    Rectangle {
        id: tools
        width: parent.width
        height: 130
        color: "#2b2b2b"

        Rectangle {
            width: parent.width; height: 1
            anchors.bottom: parent.bottom
            color: "#444"
        }

        property color paintColor: "#33B5E5"
        property int thickness: 3

        Column {
            id: colorsGroup
            anchors.left: parent.left
            anchors.leftMargin: 20
            anchors.verticalCenter: parent.verticalCenter
            spacing: 10

            Text {
                text: "ЦВЕТ"
                color: "#888"
                font.pixelSize: 11
                font.bold: true
                font.letterSpacing: 1
            }

            Row {
                spacing: 10

                Repeater {
                    model: ["#33B5E5", "#99CC00", "#FFBB33", "#FF4444",
                            "#AA66CC", "#FF8800", "#5806b0", "#000000"]

                    Rectangle {
                        width: 34; height: 34
                        radius: width / 2
                        color: modelData
                        border.width: (tools.paintColor === modelData && !root.eraserMode) ? 3 : 1
                        border.color: (tools.paintColor === modelData && !root.eraserMode) ? "white" : "#555"

                        scale: colorMa.pressed ? 0.88 : 1
                        Behavior on scale { NumberAnimation { duration: 100 } }

                        MouseArea {
                            id: colorMa
                            anchors.fill: parent
                            cursorShape: Qt.PointingHandCursor
                            onClicked: {
                                tools.paintColor = modelData
                                root.eraserMode = false
                            }
                        }
                    }
                }
            }
        }

        Column {
            id: thicknessGroup
            anchors.left: colorsGroup.right
            anchors.leftMargin: 30
            anchors.verticalCenter: parent.verticalCenter
            spacing: 10

            Text {
                text: "ТОЛЩИНА: " + tools.thickness
                color: "#888"
                font.pixelSize: 11
                font.bold: true
                font.letterSpacing: 1
            }

            Row {
                spacing: 8

                Repeater {
                    model: [1, 3, 5]

                    Rectangle {
                        width: 40; height: 34
                        radius: 8
                        color: tools.thickness === modelData ? "#33B5E5" : "#3d3d3d"
                        border.width: 1
                        border.color: tools.thickness === modelData ? "#33B5E5" : "#555"

                        Text {
                            anchors.centerIn: parent
                            text: modelData
                            color: tools.thickness === modelData ? "white" : "#ccc"
                            font.pixelSize: 12
                            font.bold: true
                        }

                        MouseArea {
                            anchors.fill: parent
                            cursorShape: Qt.PointingHandCursor
                            onClicked: tools.thickness = modelData
                        }
                    }
                }
            }
        }

        Column {
            id: actionsGroup
            anchors.right: parent.right
            anchors.rightMargin: 20
            anchors.verticalCenter: parent.verticalCenter
            spacing: 10

            Text {
                text: "ИНСТРУМЕНТЫ"
                color: "#888"
                font.pixelSize: 11
                font.bold: true
                font.letterSpacing: 1
                anchors.right: parent.right
            }

            Row {
                spacing: 8
                anchors.right: parent.right

                Pill {
                    label: "Ластик"
                    width: 90
                    active: root.eraserMode
                    activeColor: "#FF4444"
                    onClicked: root.eraserMode = !root.eraserMode
                }

                Pill {
                    label: "Очистить"
                    width: 110
                    onClicked: root.clearCanvas()
                }

                Pill {
                    label: "Сохранить"
                    width: 120
                    active: true
                    activeColor: "#33B5E5"
                    onClicked: root.saveNow()
                }

                Pill {
                    label: root.autosaveOn ? "Автосейв: вкл" : "Автосейв: выкл"
                    width: 150
                    active: root.autosaveOn
                    activeColor: "#2e7d32"
                    onClicked: root.autosaveOn = !root.autosaveOn
                }
            }
        }
    }

    Rectangle {
        id: canvasArea
        anchors {
            left: parent.left
            right: parent.right
            top: tools.bottom
            bottom: parent.bottom
            margins: 8
        }
        color: "white"
        border.width: 1
        border.color: "#444"

        Canvas {
            id: canvas
            anchors.fill: parent

            property real lastX
            property real lastY
            property color drawColor: root.eraserMode ? "white" : tools.paintColor

            function resetCanvas() {
                var ctx = getContext("2d")
                ctx.clearRect(0, 0, width, height)
                requestPaint()
            }

            onPaint: {
                var ctx = getContext("2d")
                ctx.lineWidth = tools.thickness
                ctx.strokeStyle = canvas.drawColor
                ctx.lineCap = "round"
                ctx.lineJoin = "round"
                ctx.beginPath()
                ctx.moveTo(lastX, lastY)
                lastX = paint_area.mouseX
                lastY = paint_area.mouseY
                ctx.lineTo(lastX, lastY)
                ctx.stroke()
            }
        }

        MouseArea {
            id: paint_area
            anchors.fill: parent
            hoverEnabled: true
            cursorShape: Qt.BlankCursor

            onPressed: {
                canvas.lastX = mouseX
                canvas.lastY = mouseY
            }

            onPositionChanged: {
                root.cursorPos = Qt.point(mouseX, mouseY)
                if (pressed) {
                    canvas.requestPaint()
                    root.hasDrawn = true
                }
            }

            onEntered: root.cursorVisible = true
            onExited: root.cursorVisible = false
        }

        Item {
            id: customCursor
            width: Math.max(24, tools.thickness * 2 + 12)
            height: width
            x: paint_area.mouseX - width / 2
            y: paint_area.mouseY - height / 2
            visible: root.cursorVisible

            Image {
                id: cursorImage
                anchors.fill: parent
                source: "cursor.png"
                fillMode: Image.PreserveAspectFit
                smooth: true
                visible: status === Image.Ready
            }

            Rectangle {
                anchors.centerIn: parent
                width: Math.max(6, tools.thickness)
                height: width
                radius: width / 2
                color: root.eraserMode ? "#888" : tools.paintColor
                border.width: 1
                border.color: root.eraserMode ? "#333" : Qt.darker(tools.paintColor, 1.5)
                visible: cursorImage.status !== Image.Ready
            }
        }

        Rectangle {
            anchors.horizontalCenter: parent.horizontalCenter
            anchors.bottom: parent.bottom
            anchors.bottomMargin: 20
            width: toastLabel.implicitWidth + 30
            height: 36
            radius: 18
            color: "#222"
            border.width: 1
            border.color: "#444"
            opacity: root.toastVisible ? 0.95 : 0
            visible: opacity > 0

            Behavior on opacity { NumberAnimation { duration: 200 } }

            Text {
                id: toastLabel
                anchors.centerIn: parent
                color: "white"
                font.pixelSize: 13
                font.bold: true
                text: root.toastText
            }
        }
    }

    component Pill: Rectangle {
        id: pill

        property string label: ""
        property bool active: false
        property color activeColor: "#33B5E5"
        signal clicked

        height: 34
        radius: 8
        color: active ? activeColor : "#3d3d3d"
        border.width: 1
        border.color: active ? activeColor : "#555"

        Behavior on color { ColorAnimation { duration: 120 } }

        Text {
            anchors.centerIn: parent
            text: pill.label
            color: "white"
            font.pixelSize: 12
            font.bold: true
        }

        MouseArea {
            anchors.fill: parent
            cursorShape: Qt.PointingHandCursor
            onClicked: pill.clicked()
        }
    }
}