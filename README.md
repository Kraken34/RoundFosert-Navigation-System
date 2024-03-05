# RoundFosert-Navigation-System

<b> AStart.py </b> - строит собственно путь. Здесь в верхей части файла регулируются параметры внешнего вида карты. Если программа будет медлено работать, следует именьшить разрешение карты

<b> VectorBuilder.py </b> - здесь по маршруту созданным AStart.py, строится вектор скоростей. В верхей части файла регулируются параметры скорости

<b> main.py </b> - небольшой тестовый пример работы системы. Создаёт окно с картой. Стрелочками (влево, вправо) на клавиатуре можно передвигать аппарат на единицу времени (назад, вперёд)

<b> Текущий формат вектора скорости: </b> <br>
массив[2][3], где <br>
массив[0] = [скорость X, скорость Y, скорость Z] в ГСК <br>
массив[1] = [0, 0, угловая скорость] - если скорость положительно, то это поворот направо, иначе на лево <br>
