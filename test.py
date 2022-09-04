import math
import os


class BMP:
    HEADER_SIZE = 54

    def __init__(self, array_size, width, height):
        self.headers = self.bitmap_header(array_size) + self.dib_header(array_size, width, height)

    @staticmethod
    def bitmap_header(array_size):
        # Overall size 14 bytes
        header = bytearray()

        header.extend(b'BM')  # Starting constant
        header.extend(array_size.to_bytes(4, byteorder='little'))  # size of the BMP file in bytes
        header.extend(bytes(4))  # reserved
        header.extend(BMP.HEADER_SIZE.to_bytes(4, byteorder='little'))  # offset of first byte with bitmap image data
        return header

    @staticmethod
    def dib_header(array_size, width, height):
        # Overall size 40 bytes
        header = bytearray()

        header.extend((40).to_bytes(4, byteorder='little'))  # the size of this header, in bytes (40)
        header.extend(width.to_bytes(4, byteorder='little'))  # the bitmap width in pixels
        header.extend(height.to_bytes(4, byteorder='little'))  # the bitmap height in pixels
        header.extend((1).to_bytes(2, byteorder='little'))  # the number of color planes (must be 1)
        header.extend((24).to_bytes(2, byteorder='little'))  # the number of bits per pixel
        header.extend(bytes(4))  # the compression method being used
        header.extend((array_size - BMP.HEADER_SIZE).to_bytes(4, byteorder='little'))  # the image size
        header.extend(bytes(4))  # the horizontal resolution of the image, used for printer - omitted
        header.extend(bytes(4))  # the vertical resolution of the image, used for printer - omitted
        header.extend(bytes(4))  # the number of colors in the color palette, or 0 to default to 2n
        header.extend(bytes(4))  # the number of important colors used, or 0 when every color is important
        return header

    @staticmethod
    def space(data_amount):
        if data_amount % 12 == 0:
            return data_amount
        return data_amount + (4 - (data_amount % 4))


def rectangle(data, sides_ratio):

    space = BMP.space(len(data))

    height = math.sqrt(space / sides_ratio)
    width = math.ceil(height * sides_ratio)
    height = math.ceil(height)

    space = BMP.space(3*width)*height

    missing_bytes = space - len(data)
    print(len(data), space, missing_bytes)

    data += bytes(missing_bytes)

    with open('test_files/rectangle_right.bmp', 'wb') as f:
        f.write(BMP(54+len(data), width, height).headers+data)


def line(data):

    string_space = len(data) + (4 - (len(data) % 4))

    data += bytes(string_space - len(data))

    image_width = string_space // 4

    with open('test_files/line_right.bmp', 'wb') as f:
        f.write(BMP(54+len(data), image_width, 1).headers+data)


def compare(tested):
    with open(f'test_files/{tested}_test.bmp', 'rb') as f:
        tested_object = f.read()

    with open(f'test_files/{tested}_right.bmp', 'rb') as f:
        right_object = f.read()

    diffs = []
    for i, (a, b) in enumerate(zip(tested_object, right_object)):
        if a != b:
            diffs.append(i)


if __name__ == '__main__':
    user_path = r'D:\Desktop\test.bmp'
    user_input = b'''
                                  _______
                           _,,ad8888888888bba,_
                        ,ad88888I888888888888888ba,
                      ,88888888I88888888888888888888a,
                    ,d888888888I8888888888888888888888b,
                   d88888PP"""" ""YY88888888888888888888b,
                 ,d88"'__,,--------,,,,.;ZZZY8888888888888,
                ,8IIl'"                ;;l"ZZZIII8888888888,
               ,I88l;'                  ;lZZZZZ888III8888888,
             ,II88Zl;.                  ;llZZZZZ888888I888888,
            ,II888Zl;.                .;;;;;lllZZZ888888I8888b
           ,II8888Z;;                 `;;;;;''llZZ8888888I8888,
           II88888Z;'                        .;lZZZ8888888I888b
           II88888Z; _,aaa,      .,aaaaa,__.l;llZZZ88888888I888
           II88888IZZZZZZZZZ,  .ZZZZZZZZZZZZZZ;llZZ88888888I888,
           II88888IZZ<'(@@>Z|  |ZZZ<'(@@>ZZZZ;;llZZ888888888I88I
          ,II88888;   `""" ;|  |ZZ; `"""     ;;llZ8888888888I888
          II888888l            `;;          .;llZZ8888888888I888,
         ,II888888Z;           ;;;        .;;llZZZ8888888888I888I
         III888888Zl;    ..,   `;;       ,;;lllZZZ88888888888I888
         II88888888Z;;...;(_    _)      ,;;;llZZZZ88888888888I888,
         II88888888Zl;;;;;' `--'Z;.   .,;;;;llZZZZ88888888888I888b
         ]I888888888Z;;;;'   ";llllll;..;;;lllZZZZ88888888888I8888,
         II888888888Zl.;;"Y88bd888P";;,..;lllZZZZZ88888888888I8888I
         II8888888888Zl;.; `"PPP";;;,..;lllZZZZZZZ88888888888I88888
         II888888888888Zl;;. `;;;l;;;;lllZZZZZZZZW88888888888I88888
         `II8888888888888Zl;.    ,;;lllZZZZZZZZWMZ88888888888I88888
          II8888888888888888ZbaalllZZZZZZZZZWWMZZZ8888888888I888888,
          `II88888888888888888b"WWZZZZZWWWMMZZZZZZI888888888I888888b
           `II88888888888888888;ZZMMMMMMZZZZZZZZllI888888888I8888888
            `II8888888888888888 `;lZZZZZZZZZZZlllll888888888I8888888,
             II8888888888888888, `;lllZZZZllllll;;.Y88888888I8888888b,
            ,II8888888888888888b   .;;lllllll;;;.;..88888888I88888888b,
            II888888888888888PZI;.  .`;;;.;;;..; ...88888888I8888888888,
            II888888888888PZ;;';;.   ;. .;.  .;. .. Y8888888I88888888888b,
           ,II888888888PZ;;'                        `8888888I8888888888888b,
           II888888888'                              888888I8888888888888888b
          ,II888888888                              ,888888I88888888888888888
         ,d88888888888                              d888888I8888888888ZZZZZZZ
      ,ad888888888888I                              8888888I8888ZZZZZZZZZZZZZ
    ,d888888888888888'                              888888IZZZZZZZZZZZZZZZZZZ
  ,d888888888888P'8P'                               Y888ZZZZZZZZZZZZZZZZZZZZZ
 ,8888888888888,  "                                 ,ZZZZZZZZZZZZZZZZZZZZZZZZ
d888888888888888,                                ,ZZZZZZZZZZZZZZZZZZZZZZZZZZZ
888888888888888888a,      _                    ,ZZZZZZZZZZZZZZZZZZZZ888888888
888888888888888888888ba,_d'                  ,ZZZZZZZZZZZZZZZZZ88888888888888
8888888888888888888888888888bbbaaa,,,______,ZZZZZZZZZZZZZZZ888888888888888888
88888888888888888888888888888888888888888ZZZZZZZZZZZZZZZ888888888888888888888
8888888888888888888888888888888888888888ZZZZZZZZZZZZZZ88888888888888888888888
888888888888888888888888888888888888888ZZZZZZZZZZZZZZ888888888888888888888888
8888888888888888888888888888888888888ZZZZZZZZZZZZZZ88888888888888888888888888
88888888888888888888888888888888888ZZZZZZZZZZZZZZ8888888888888888888888888888
8888888888888888888888888888888888ZZZZZZZZZZZZZZ88888888888888888 Normand  88
88888888888888888888888888888888ZZZZZZZZZZZZZZ8888888888888888888 Veilleux 88
8888888888888888888888888888888ZZZZZZZZZZZZZZ88888888888888888888888888888888

    '''
    sides_ratio = 1

    if not os.path.isdir("test_files"):
        os.mkdir("test_files")

    line(user_input)
    compare('line')

    rectangle(user_input, sides_ratio)
    compare('rectangle')
    # Not in a working state
