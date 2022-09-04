import math
import os
import random

# TODO: implement random bytes selection instead of just appending \x00 bytes
UNPRINTABLE_CHARACTERS = [b'\x00', b'\x02', b'\t', b'\n', b'\r', b'\x1b',
                          b'\x1c', b'\x1d', b'\x1e', b'\x1f', b' ', b'\xa0']

class BMP:
    HEADER_SIZE = 54

    def __init__(self, array_size, width, height):
        self.headers = self.bitmap_header(array_size) + self.dib_header(array_size, width, height)

    @staticmethod
    def bitmap_header(array_size):
        # Overall size of 14 bytes
        header = bytearray()

        header.extend(b'BM')  # Starting constant
        header.extend(array_size.to_bytes(4, byteorder='little'))  # size of the BMP file in bytes
        header.extend(bytes(4))  # reserved
        header.extend(BMP.HEADER_SIZE.to_bytes(4, byteorder='little'))  # offset of first byte with bitmap image data
        return header

    @staticmethod
    def dib_header(array_size, width, height):
        # Overall size of 40 bytes
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


class Rectangle:
    def __init__(self, sides_ratio, needed_space):
        self.sides_ratio = sides_ratio
        self.width = None
        self.height = None
        self.set_width_and_height(needed_space)

    def __iter__(self):
        return iter((self.width, self.height))

    def set_width_and_height(self, needed_space):
        height = math.sqrt(needed_space / self.sides_ratio)
        self.width = math.ceil(height * self.sides_ratio)
        self.height = math.ceil(height)


class Image:
    def __init__(self, data, sides_ratio=None):
        self.data = data
        self.sides_ratio = sides_ratio
        self.rectangle = None
        # TODO this is a naming disaster, needs to be refactored
        self.string_space = self.calculate_string_space()
        self.needed_space = BMP.HEADER_SIZE + self.string_space
        self.overall_space = self.calculate_overall_space()
        self.padding_space = self.calculate_padding()

    def create_rectangle_object(self):
        # TODO is there not a better solution?
        self.rectangle = Rectangle(self.sides_ratio, self.needed_space)
        return self.rectangle

    def calculate_string_space(self):
        if not self.sides_ratio:
            return BMP.space(len(self.data))
        return len(self.data)

    def calculate_overall_space(self):
        """
        Calculates combined taken space by headers, input data, and padding.
        If the outputted shape is a line it is equal to the variable self.needed_space.
        """
        if not self.sides_ratio:
            return BMP.HEADER_SIZE + self.string_space

        width, height = self.create_rectangle_object().__iter__()
        return BMP.HEADER_SIZE + BMP.space(3*width) * height

    def calculate_padding(self):
        if not self.sides_ratio:
            return self.string_space - len(self.data)
        return self.overall_space - self.string_space

    def calculate_chars_ratio(self):
        characters = {}

        for char in self.data:
            if char not in characters:
                characters[char] = 0
            else:
                characters[char] += 1

        ratio = {key: occurrences/len(self.data) for key, occurrences in characters.items()}
        return ratio

    def padding_based_on_chars_ratio(self):
        characters_ratio = self.calculate_chars_ratio()
        print(characters_ratio)
        characters = [key.to_bytes(1, byteorder='little')*int(ratio*self.padding_space)
                      for key, ratio in characters_ratio.items()]
        return characters

    def random_padding(self):
        # TODO: group all possible variants and let user choose
        # return b''.join(random.choices(UNPRINTABLE_CHARACTERS, k=self.padding_space))
        # return b''.join([i.to_bytes(1, byteorder='little') for i in random.choices(self.data, k=self.padding_space)])
        # return b''.join(random.sample(self.padding_based_on_chars_ratio(), k=len(self.padding_based_on_chars_ratio())))
        return random.randbytes(self.padding_space)

    def write(self, name, specified_path=None):

        name = f"{name}.bmp" if not name.endswith(".bmp") else name
        path = os.path.join(specified_path, name) if specified_path else name

        if not self.sides_ratio:
            bmp_data = BMP(self.overall_space, self.string_space//4, 1)
        else:
            bmp_data = BMP(self.overall_space, self.rectangle.width, self.rectangle.height)

        image_data = bmp_data.headers + self.data + self.random_padding()

        with open(path, 'wb') as f:
            f.write(image_data)


if __name__ == '__main__':
    user_path = r'D:\Desktop'
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
    img = Image(user_input, sides_ratio)
    img.write("test", user_path)
