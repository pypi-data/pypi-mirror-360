import simplygame as SG
x = 400
y = 300
running = True
pressed = False
keys = []
GREEN = (0,255,0)
###
#current_path = 'C:/Users/FlowUP/Desktop/simplygame/simplygame'
image = SG.load_image("simply.png")
###

SG.create_window("test", 800,600)

while running:
    event = SG.recover_event()
    if event == 'exit':
        running = False
   
    SG.draw_rect(0,0,50,50,GREEN)
    SG.draw_image(image, 0,0,255)

    SG.tick(60)
    SG.update()