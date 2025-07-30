import base64
import binascii

from Crypto.Util.Padding import pad
from Crypto.Cipher import AES


class BaseEncode(object):

    def __init__(self):
        pass

    @classmethod
    def get_byte_md5_value(cls, bytes):
        """
        获得byte md5值
        :param bytes:需要操作的二进制
        :return:
        """
        import hashlib
        myMd5 = hashlib.md5(bytes)
        myMd5_Digest = myMd5.hexdigest()
        return myMd5_Digest

    @classmethod
    def get_md5_value(cls, src):
        """
        获得字符串md5值
        :param src:需要操作的字符串
        :return:
        """
        import hashlib
        myMd5 = hashlib.md5()
        myMd5.update(src.encode("utf8"))
        myMd5_Digest = myMd5.hexdigest()
        return myMd5_Digest

    @classmethod
    def get_md5_value_16bit(cls, src):
        """
        获取16位md5
        :param src:
        :return:
        """
        return cls.get_md5_value(src)[8:-8]

    @classmethod
    def get_byte_md5_value_16bit(cls, bytes):
        """
        获取16位md5
        :param bytes:
        :return:
        """
        return cls.get_byte_md5_value(bytes)[8:-8]

    @classmethod
    def get_sha1_value(cls, src):
        """
         获得字符串sha1值
        :param src:
        :return:
        """
        import hashlib
        mySha1 = hashlib.sha1()
        mySha1.update(src)
        mySha1_Digest = mySha1.hexdigest()
        return mySha1_Digest

    @classmethod
    def get_base64(cls, src):
        """
        输入字符串，编码成base64
        :param src:
        :return:
        """
        strEncode = base64.b64encode(src.encode('utf8')).decode('utf8')
        return strEncode

    @classmethod
    def base64_get_str(cls, base64_str):
        """
        输入base64字符串，输出原始字符串
        :param base64_str:
        :return:
        """
        src = base64.b64decode(base64_str.encode('utf8')).decode('utf8')
        return src

    @classmethod
    def aes_encode(cls, password, text, mode, iv=None):
        """
         https://blog.csdn.net/qq_42334096/article/details/122847876
        在AES标准规范中，分组长度只能是128位 每个分组为16个字节(每个字节8位)。
        密钥长度可以使用128位、192位或256位。密钥的长度不同，推荐加密轮数也不同。
        AES	密钥长度(32位比特字)	分组长度(32位比特字)	加密轮数
        AES-128	4	4	10
        AES-192	6	4	11
        AES-256	8	4	14
        填充模式：这是因为如果明文不是128位(16字节)的则需要进行填充，需要将明文补充到16个字节整数倍的长度。在我们进行加解密时需要采用同样的填充方式，
        否则无法解密成功。填充模式有：No Padding、PKCS5 Padding、PKCS7 Padding、ISO10126 Padding、Ansix923 Padding、Zero Padding等等。
        pip install pycryptodome
        （亲测，目前不用改文件夹名字了） 但是，在使用的时候导包是有问题的，这个时候只要修改一个文件夹的名称就可以完美解决这个问题
        C:\用户\Administrator\AppData\Local\Programs\Python\Python36\Lib\site-packages

        找到这个路径，下面有一个文件夹叫做crypto,将c改成C，对就是改成大写就ok了！
        liunx: pip install pycrypto
        :param password:
        :param text:
        :param mode:
        :return:
        """
        if mode == AES.MODE_ECB:
            assert len(password) % 16 == 0, Exception("密匙 位数应该为16的倍数")
            assert len(text) % 16 == 0, Exception("加密文本 位数应该为16的倍数")
            # MODE_ECB 秘钥必须为16字节或者16字节的倍数的字节型数据。
            # MODE_ECB 明文必须为16字节或者16字节的倍数的字节型数据，如果不够16字节需要进行补全，关于补全规则，后面会在补全模式中具体介绍。
            aes = AES.new(password, AES.MODE_ECB)  # 创建一个aes对象
            # AES.MODE_ECB 表示模式是ECB模式
            en_text = aes.encrypt(text)  # 加密明文
            return en_text
        if mode == AES.MODE_CBC:
            # 1. 在Python中进行AES加密解密时，所传入的密文、明文、秘钥、iv偏移量、都需要是bytes（字节型）数据。python 在构建aes对象时也只能接受bytes类型数据。
            # 2.当秘钥，iv偏移量，待加密的明文，字节长度不够16字节或者16字节倍数的时候需要进行补全。
            # 3. CBC模式需要重新生成AES对象，为了防止这类错误，我写代码无论是什么模式都重新生成AES对象。
            assert iv is not None
            aes = AES.new(password, AES.MODE_CBC, iv)  # 创建一个aes对象
            # AES.MODE_CBC 表示模式是CBC模式
            en_text = aes.encrypt(text)
            return en_text

    @classmethod
    def aes_decode(cls, password, en_text, mode, iv=None):
        """
        :return:
        """
        if mode == AES.MODE_ECB:
            assert len(password) % 16 == 0, Exception("密匙 位数应该为16的倍数")
            assert len(en_text) % 16 == 0, Exception("密文 位数应该为16的倍数")
            aes = AES.new(password, AES.MODE_ECB)  # 创建一个aes对象
            # AES.MODE_ECB 表示模式是ECB模式
            text = aes.decrypt(en_text)  # 加密明文
            return text
        if mode == AES.MODE_CBC:
            assert iv is not None
            aes = AES.new(password, AES.MODE_CBC, iv)  # 创建一个aes对象
            # AES.MODE_CBC 表示模式是CBC模式
            text = aes.decrypt(en_text)
            return text


# 数据类
class MData():
    def __init__(self, data=b"", characterSet='utf-8'):
        # data肯定为bytes
        self.data = data
        self.characterSet = characterSet

    def saveData(self, FileName):
        with open(FileName, 'wb') as f:
            f.write(self.data)

    def fromString(self, data):
        self.data = data.encode(self.characterSet)
        return self.data

    def fromBase64(self, data):
        self.data = base64.b64decode(data.encode(self.characterSet))
        return self.data

    def fromHexStr(self, data):
        self.data = binascii.a2b_hex(data)
        return self.data

    def toString(self):
        return self.data.decode(self.characterSet)

    def toBase64(self):
        return base64.b64encode(self.data).decode()

    def toHexStr(self):
        return binascii.b2a_hex(self.data).decode()

    def toBytes(self):
        return self.data

    def __str__(self):
        try:
            return self.toString()
        except Exception:
            return self.toBase64()


### 封装类
class AEScryptor():
    def __init__(self, key, mode, iv='', paddingMode="NoPadding", characterSet="utf-8"):
        '''
        构建一个AES对象
        key: 秘钥，字节型数据
        mode: 使用模式，只提供两种，AES.MODE_CBC, AES.MODE_ECB
        iv： iv偏移量，字节型数据
        paddingMode: 填充模式，默认为NoPadding, 可选NoPadding，ZeroPadding，PKCS5Padding，PKCS7Padding
        characterSet: 字符集编码
        '''
        self.key = key
        self.mode = mode
        self.iv = iv
        self.characterSet = characterSet
        self.paddingMode = paddingMode
        self.data = ""

    def __ZeroPadding(self, data):
        data += b'\x00'
        while len(data) % 16 != 0:
            data += b'\x00'
        return data

    def __StripZeroPadding(self, data):
        data = data[:-1]
        while len(data) % 16 != 0:
            data = data.rstrip(b'\x00')
            if data[-1] != b"\x00":
                break
        return data

    def __PKCS5_7Padding(self, data):
        needSize = 16 - len(data) % 16
        if needSize == 0:
            needSize = 16
        return data + needSize.to_bytes(1, 'little') * needSize

    def __StripPKCS5_7Padding(self, data):
        paddingSize = data[-1]
        return data.rstrip(paddingSize.to_bytes(1, 'little'))

    def __paddingData(self, data):
        if self.paddingMode == "NoPadding":
            if len(data) % 16 == 0:
                return data
            else:
                return self.__ZeroPadding(data)
        elif self.paddingMode == "ZeroPadding":
            return self.__ZeroPadding(data)
        elif self.paddingMode == "PKCS5Padding" or self.paddingMode == "PKCS7Padding":
            return self.__PKCS5_7Padding(data)
        else:
            print("不支持Padding")

    def __stripPaddingData(self, data):
        if self.paddingMode == "NoPadding":
            return self.__StripZeroPadding(data)
        elif self.paddingMode == "ZeroPadding":
            return self.__StripZeroPadding(data)

        elif self.paddingMode == "PKCS5Padding" or self.paddingMode == "PKCS7Padding":
            return self.__StripPKCS5_7Padding(data)
        else:
            print("不支持Padding")

    def setCharacterSet(self, characterSet):
        '''
        设置字符集编码
        characterSet: 字符集编码
        '''
        self.characterSet = characterSet

    def setPaddingMode(self, mode):
        '''
        设置填充模式
        mode: 可选NoPadding，ZeroPadding，PKCS5Padding，PKCS7Padding
        '''
        self.paddingMode = mode

    def decryptFromBase64(self, entext):
        '''
        从base64编码字符串编码进行AES解密
        entext: 数据类型str
        '''
        mData = MData(characterSet=self.characterSet)
        self.data = mData.fromBase64(entext)
        return self.__decrypt()

    def decryptFromHexStr(self, entext):
        '''
        从hexstr编码字符串编码进行AES解密
        entext: 数据类型str
        '''
        mData = MData(characterSet=self.characterSet)
        self.data = mData.fromHexStr(entext)
        return self.__decrypt()

    def decryptFromString(self, entext):
        '''
        从字符串进行AES解密
        entext: 数据类型str
        '''
        mData = MData(characterSet=self.characterSet)
        self.data = mData.fromString(entext)
        return self.__decrypt()

    def decryptFromBytes(self, entext):
        '''
        从二进制进行AES解密
        entext: 数据类型bytes
        '''
        self.data = entext
        return self.__decrypt()

    def encryptFromString(self, data):
        '''
        对字符串进行AES加密
        data: 待加密字符串，数据类型为str
        '''
        self.data = data.encode(self.characterSet)
        return self.__encrypt()

    def __encrypt(self):
        if self.mode == AES.MODE_CBC:
            aes = AES.new(self.key, self.mode, self.iv)
        elif self.mode == AES.MODE_ECB:
            aes = AES.new(self.key, self.mode)
        else:
            print("不支持这种模式")
            return

        data = self.__paddingData(self.data)
        enData = aes.encrypt(data)
        return MData(enData)

    def __decrypt(self):
        if self.mode == AES.MODE_CBC:
            aes = AES.new(self.key, self.mode, self.iv)
        elif self.mode == AES.MODE_ECB:
            aes = AES.new(self.key, self.mode)
        else:
            print("不支持这种模式")
            return
        data = aes.decrypt(self.data)
        mData = MData(self.__stripPaddingData(data), characterSet=self.characterSet)
        return mData


# if __name__ == '__main__':
#     key = b"1234567812345678"
#     iv = b"0000000000000000"
#     aes = AEScryptor(key, AES.MODE_CBC, iv, paddingMode="ZeroPadding", characterSet='utf-8')
#
#     data = "好好学习"
#     rData = aes.encryptFromString(data)
#     print("密文：", rData.toBase64())
#     rData = aes.decryptFromBase64(rData.toBase64())
#     print("明文：", rData)
