import math

# To run this script use command: python pathToScript outputPath imageData

path = r'D:\Desktop\test.bmp'
data = b'''
\xff\xff\xff\x00\x00\x00\xff\xff\xff
\xff\xff\xff\x00\x00\x00\xff\xff\xff
\xff\xff\xff\x00\x00\x00\xff\xff\xff
\xff\xff\xff\x00\x00\x00\xff\xff\xff
'''


class Image:
    def __init__(self, path, height, data):
        self.path = path
        self.neededSpace = self.space(data)
        self.height = height
        self.width = self.neededSpace // 4
        self.data = self.appendData(data)


    def space(self, data):
        dataLength = len(data)
        return dataLength + (4 - (dataLength % 4))

    def appendData(self, data):
        data += bytes(self.neededSpace - len(self.data))
        return data


def calculateNeededSpace(amount):
    if amount % 12 == 0:
        return amount
    return amount + (4 - (amount % 4))


sidesRatio = 4/3

space = calculateNeededSpace(len(data))

height = math.sqrt(space / sidesRatio)
width = math.ceil(height * sidesRatio)
height = math.ceil(height)

space = calculateNeededSpace(width*height)

numberOfBytes = 3 * width
missingBytes = height * (calculateNeededSpace(numberOfBytes) - numberOfBytes)

data += bytes(missingBytes)

imgData = bytearray()


def line():
    imageHeight = 1

    dataLength = len(data)
    spaceForString = dataLength + (4 - (dataLength % 4))

    data += bytes(spaceForString - dataLength)

    imageWidth = spaceForString // 4
    rowSize = math.ceil((24 * imageWidth) / 32) * 4
    pixelArraySize = rowSize * imageHeight - 250


def bitmapHeaders():
    # Bitmap file headers
    imgData.extend(b'BM')  # Starting constant
    imgData.extend((pixelArraySize + 54).to_bytes(4, byteorder='little'))  # size of the BMP file in bytes
    imgData.extend(bytes(4))  # reserved
    imgData.extend((54).to_bytes(4, byteorder='little'))  # offset of first byte with bitmap image data

def DIBHeaders():
    # DIB headers
    imgData.extend((40).to_bytes(4, byteorder='little'))  # the size of this header, in bytes (40)
    imgData.extend(imageWidth.to_bytes(4, byteorder='little'))  # the bitmap width in pixels
    imgData.extend(imageHeight.to_bytes(4, byteorder='little'))  # the bitmap height in pixels
    imgData.extend((1).to_bytes(2, byteorder='little'))  # the number of color planes (must be 1)
    imgData.extend((24).to_bytes(2, byteorder='little'))  # the number of bits per pixel
    imgData.extend(bytes(4))  # the compression method being used
    imgData.extend(pixelArraySize.to_bytes(4, byteorder='little'))  # the image size
    imgData.extend(bytes(4))  # the horizontal resolution of the image, may need to be changed (same for the lower one)?
    imgData.extend(bytes(4))  # the vertical resolution of the image
    imgData.extend(bytes(4))  # the number of colors in the color palette, or 0 to default to 2n
    imgData.extend(bytes(4))  # the number of important colors used, or 0 when every color is important


# if __name__ == '__main__':
#     bitmapHeaders()
#     DIBHeaders()
#     imgData.extend(data)
#     with open(path, 'wb') as f:
#         f.write(imgData)
