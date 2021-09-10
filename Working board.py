from random import randint


class GameBoardException(Exception):  # корневой класс исключений
    pass


class GameBoardOutException(GameBoardException):  # вызываем исключение когда стреляем за пределы доски
    def __str__(self):
        return "The shot is out of the field, hawkeye"


class GameBoardUsedException(GameBoardException):  # вызываем исключение когда в эту точку уже стреляли
    def __str__(self):
        return "You have chosen this spot already"


class GameBoardWrongShipException(GameBoardException):
    pass


class Dot:   # класс о точке на доске
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):  # проверка точек на равенство
        return self.x == other.x and self.y == other.y

    def __repr__(self):  # отображение точки на доске для передачи в другие классы
        return f"Dot({self.x}, {self.y})"


class Ship:    # класс корабля
    def __init__(self, bow, length, orientation):  # нос, длина корабля и куда направлен
        self.bow = bow
        self.length = length
        self.orientation = orientation
        self.lives = length

    @property
    def dots(self):  # список точек которые корабль занимает
        ship_dots = []
        for i in range(self.length):
            cur_x = self.bow.x
            cur_y = self.bow.y
            if self.orientation == 0:  # вертикальканая ориентация
                cur_x += i
            elif self.orientation == 1:  # горизонтальная ориентация
                cur_y += i
            ship_dots.append(Dot(cur_x, cur_y))
        return ship_dots

    def shooten(self, shot):  # проверяем попали мы в корабль или нет
        return shot in self.dots


class Board:   # класс доски
    def __init__(self, hid=False, size=7):  # размер доски и видим ли мы подстреленные корабли противника
        self.size = size
        self.hid = hid
        self.count = 0  # сколько кораблей на доске уничтожено
        self.field = [["O"] * size for _ in range(size)]  # формируем вид доски
        self.busy = []  # точки которые уже заняты
        self.ships = []  # корабли на доске

    def __str__(self):  # отображаем доску красиво
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 | 7 |"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hid:
            res = res.replace("■", "O")
        return res

    def out(self, d):  # проверяем не вышла ли точка за границы доски
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def contour(self, ship, verb=False):  # захватываем точки рядом с кораблем т.к. их нельзя использовать для расстановки новых кораблей
        near = [       # verb значит нужно ли помечать точками место "мимо"
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)  # текущая точка
                if not (self.out(cur)) and cur not in self.busy:  # проверяем не вышла ли точка за границы доски и не занята ли
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)

    def add_ship(self, ship):  # добавляем корабли на доску
        for d in ship.dots:
            if self.out(d) or d in self.busy:  # проверяем не вышла ли точка за границы доски и не занята ли
                raise GameBoardWrongShipException()
        for d in ship.dots:  # добавляем клетки занятые кораблем + точки рядом
            self.field[d.x][d.y] = "■"
            self.busy.append(d)
        self.ships.append(ship)
        self.contour(ship)

    def shot(self, d):  # проверяем точку по которой выстрелили
        if self.out(d):  # не вышли ли за границы доски
            raise GameBoardOutException()
        if d in self.busy:  # не занята ли
            raise GameBoardUsedException()
        self.busy.append(d)  # добавляем в список занятых если все ОК
        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1  # уменьшаем кол-во жизней у корабля
                self.field[d.x][d.y] = "X"  # помечаем подстреленную часть
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Your ship has drowned!")  # указываем когда все части корабля подстрелены
                    return False
                else:
                    print("Nice shot! Make another one")
                    return True
        self.field[d.x][d.y] = "."
        print("Miss!")
        return False

    def begin(self):
        self.busy = []  # изначально список занятых точек пуст

    def defeat (self):
        return self.count == len(self.ships)


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except GameBoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"AI turn: {d.x + 1} {d.y + 1}")
        return d


class User(Player):
    def ask(self):
        while True:
            cords = input("Your turn: ").split()
            if len(cords) != 2:
                print(" input 2 coordinates ")
                continue
            x, y = cords
            if not (x.isdigit()) or not (y.isdigit()):
                print(" Input your numbers! ")
                continue
            x, y = int(x), int(y)
            return Dot(x - 1, y - 1)


class Game:
    def __init__(self, size=7):
        self.lens = [4, 3, 3, 2, 2, 2, 1, 1, 1, 1]
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True
        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def make_board(self):
        lens = [3, 2, 2, 1, 1, 1, 1]  # возможные длины кораблей
        board = Board(size=self.size)  # создаем пустую доску
        attempts = 0
        for length in self.lens:
            while True:
                attempts += 1
                if attempts > 2000:  # выход из бесконечного цикла если корабль некуда поставить
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), length, randint(0, 1))  # рандомные координаты для кораблей
                try:  # пытаемся добавить корабль на доску
                    board.add_ship(ship)
                    break
                except GameBoardWrongShipException:  # обрабатываем исключение в случае неверных координат
                    pass
        board.begin()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.make_board()
        return board

    def introduction(self):
        print("**************************************")
        print("Welcome in my little game 'SeeBattle'")
        print("You play against the AI")
        print("--------------------------------------")
        print(" format of input: x y ")
        print(" x - number of row  ")
        print(" y - number of column ")
        print("**************************************")

    def loop(self):
        num = 0
        while True:
            print("-" * 20)
            print("Your board:")
            print(self.us.board)
            print("-" * 20)
            print("AI's board:")
            print(self.ai.board)
            print("-" * 20)
            if num % 2 == 0:
                print("Your turn")
                repeat = self.us.move()
            else:
                print("AI turn!")
                repeat = self.ai.move()
            if repeat:
                num -= 1
            if self.ai.board.defeat():
                print("-" * 20)
                print("You have won")
                break
            if self.us.board.defeat():
                print("-" * 20)
                print("AI has won")
                break
            num += 1

    def start(self):
        self.introduction()
        self.loop()


g = Game()
g.start()
