
// ===============================================
// MICRO:BIT - TACHOGRAPH SIMULATOR
// ===============================================

// USB SERIAL CONNECTION

serial.redirectToUSB()
serial.setBaudRate(BaudRate.BaudRate115200)

serial.writeLine("READY")


// ===============================================
// MICRO:BIT READY
// ===============================================

basic.showIcon(IconNames.Happy)


// ===============================================
// SHAKE DETECTION
// ===============================================

input.onGesture(Gesture.Shake, function () {

    serial.writeLine("SHAKE")

    basic.showIcon(IconNames.Yes)

    basic.pause(200)

    basic.showIcon(IconNames.Happy)
})


// ===============================================
// BUTTON A - SHAKE TEST
// ===============================================

input.onButtonPressed(Button.A, function () {

    serial.writeLine("SHAKE")

    basic.showIcon(IconNames.Yes)

    basic.pause(200)

    basic.showIcon(IconNames.Happy)
})


// ===============================================
// MOTION SENSOR
// ===============================================

let oldX = input.acceleration(Dimension.X)
let oldY = input.acceleration(Dimension.Y)
let oldZ = input.acceleration(Dimension.Z)


// ===============================================
// CONTINUOUS MOTION DETECTION
// ===============================================

basic.forever(function () {

    let x = input.acceleration(Dimension.X)
    let y = input.acceleration(Dimension.Y)
    let z = input.acceleration(Dimension.Z)

    let movement =
        Math.abs(x - oldX) +
        Math.abs(y - oldY) +
        Math.abs(z - oldZ)

    if (movement > 250) {

        serial.writeLine("MOTION")
    }

    oldX = x
    oldY = y
    oldZ = z

    basic.pause(100)
})
