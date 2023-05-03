import RPi.GPIO as gpio
import time
from matplotlib import pyplot as plt

gpio.setmode(gpio.BCM)

leds=[21, 20, 16, 12, 7, 8, 25, 24]
gpio.setup(leds, gpio.OUT)

dac=[26, 19, 13, 6, 5, 11, 9, 10]
gpio.setup(dac, gpio.OUT, initial=gpio.HIGH)

comp = 4
troyka = 17 
gpio.setup(troyka, gpio.OUT, initial=gpio.HIGH)
gpio.setup(comp, gpio.IN)

#снятие показаний с тройки модуля
def adc():
    k=0
    for i in range(7, -1, -1):
        k+=2**i
        gpio.output(dac, dec_to_bin(k))
        time.sleep(0.001)
        if gpio.input(comp)==0:
            k-=2**i
    return k

def dec_to_bin(a):
    return [int (elem) for elem in bin(a)[2:].zfill(8)]

try:
    voltage=0
    measure_res=[]
    
    count=0
    
    voltage=adc()

    while voltage > 0:
        voltage=adc()
        print('нажми на кнопкууу!')
    time_start=time.time()
    while voltage < 10:
        voltage=adc()
        measure_res.append(voltage)
        time.sleep(0)
        count+=1
        gpio.output(leds, dec_to_bin(voltage))
        #print(voltage)

    gpio.output(troyka, gpio.LOW)
    #gpio.setup(troyka, gpio.OUT, initial=gpio.HIGH)

    #зарядка конденсатора, запис показаний в процессе
    print('начало зарядки конденсатора')
    while voltage<220:
        voltage=adc()
        measure_res.append(voltage)
        time.sleep(0)
        count+=1
        gpio.output(leds, dec_to_bin(voltage))
        #print(voltage)
    gpio.output(troyka, gpio.HIGH)
    
    #разрядка конденсатора, запись показаний в процессе
    print('начало разрядки конденсатора')
    while voltage > 45:
        voltage = adc()
        measure_res.append(voltage)
        time.sleep(0)
        count += 1
        gpio.output(leds, dec_to_bin(voltage))
    time_experiment = time.time() - time_start
    
    #запись данных в файлы
    print('запись данных в файл')
    measure_res_str = [str(item) for item in measure_res]
    with open('data.txt', 'w') as f:
        f.write("\n".join(measure_res_str))
    with open('settings.txt', 'w') as f:
        f.write("".join(str(1/time_experiment/count)))
        f.write('\n0.01289')
    print('общая продолжительность эксперимента {}, период одного измерения {}, средняя частота дискретизации {}, шаг квантования АЦП {}'.format(time_experiment, time_experiment/count, 1/time_experiment/count, 0.013))
    
    #графики
    print('построение графиков')
    y=[i / 256*3.3 for i in measure_res]
    x=[i * time_experiment / count for i in range(len(measure_res))]
    plt.plot(x, y)
    plt.xlabel('время')
    plt.ylabel('вольтаж')
    plt.show()

finally:
    gpio.output(leds, 0)
    gpio.output(dac, 0)
    gpio.cleanup()