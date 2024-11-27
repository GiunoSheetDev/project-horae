animal.Animal methods:
    .loadAnimations: 
        returns a dictionary with the keys contained in the states list. Each key is a list of pygame.Images
    .getPixelDimensionOfSpriteBasedOnAnimalType: 
        adjusts attributes to draw the isometric sprites based on the animal image dimensions
    .checkNeeds: 
        sets animal state based on the hunger and thirst
    .updateNeeds: 
        updates hunger and thirst
    .setMovementStateAndSpeed: 
        based on the current state decides whether to idle, walk or run and adjusts speed accordingly
    .generatePath: 
        based on current movement state generates a random endPoint and creates a tuple (dx, dy) 
    .translatePath
        modifies the path according to the speed to have a smooth movement of the sprite
    .updatePath
        based on the first element of pathData, moves the sprite accordingly and pops the first element for the next iteration
    .handleDirectionChanges
        changes current direction based on first element of pathData
    .updateAnimation
        updates the current Frame to animate the animal
    .isBeingClicked
        returns True if animal.rect collides with the mouse
    .update
        calls all method used for update in the following order
            self.updateNeeds()
            if self.pathData == []:
                self.checkNeeds() # -> set current state based on hunger / thirst
                self.setMovementStateAndSpeed() # -> based on current state set movement state and speed
                self.generatePath() # -> based on movement state generate a path and pathData
                self.translatePath() # -> adjust pathData based on speed
        
            self.updatePath() # -> make character move
            self.updateAnimation() # -> animate character
            self.draw(screen=screen, backgroundStartingX=backgroundStartingX, backgroundStartingY=backgroundStartingY)
            self.isClicked = self.isBeingClicked(mousePos=mousePos)
        and updates the isClicked attribute
    .drawCollisionRect
        draws the border of the animal.rect
    .drawVisibilityRect
        scales the animal.rect by a factor of 5 and draws it 
    .draw
        blits the animal on screen

inputmanager.InputManager
    .handleEvents
        adds and removes pressed keys to the class sets
    .isActionPressed
        returns the state of a key
    .isMouseButtonPressed
        returns the state of a mouse button

ui.AnimalInspector
    .createDisplay
        creates a pygame.Surface with a currentStateText, currentDirectionText, hungerText, thirstText
    .draw
        blits on screen if isShowing is True
    .update
        calls createDisplay and draws on screen


                    
