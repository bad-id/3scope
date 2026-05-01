% An introduction to what a class can do in Matlab

% A class file starts with the class definition.
% Here IntroClass is the class name and handle
% is the class where it is derived from.
% This last part can be either one of the two standard
% classes 'handle' and 'value' or any other class
% from which you want to derive a class
classdef IntroClass < handle
    % Properties are like the subvariables of (an instance of)
    % the class.
    properties
        PropOne; % A variable that represents a property
        PropTwo; % Another variable that represents a property
    end
    % Dependent properties look similar from the outside
    % of a class, but have no real intrinsic value. They
    % are calculated by the get method defined below.
    % They can also be used the other way around with a set method.
    properties (Dependent)
        PropThree; % An example of a dependent property
    end
    % A constant property can be read from an instance
    % of the class, or directly from the class itself.
    % As the name suggests, they can not be modified by code
    % and are the same for any instance of the class.
    properties (Constant)
        PropFour = 12; % An example of a constant property
    end
    % Methods are the functions of a class.
    methods
        % Nearly every class has a Constructor method
        % This is used to create an instance of the class
        % and initialise it. In this case two input arguments
        % are used whose values are assigned to two properties
        % of the instance.
        function obj=IntroClass(One,Two)
            % Constructs an instance and gives values to PropOne and PropTwo
            obj.PropOne = One;
            obj.PropTwo = Two;
        end
        % A more-or-less standard function in a class.
        % It gets the instance of the class (obj) as
        % input argument, as well as an extra input.
        % The results will depend on PropOne and can
        % therefore be different for any instance of the class
        function Output = FunctionOne(obj, InputOne)
            % Averages the input variable with InputOne
            Output = (obj.PropOne + InputOne) ./ 2;
        end
        % The function to read the dependent property
        % PropThree. Whenever the value of PropThree of
        % an instance of the class is called, this function
        % will be used to calculate it.
        function P3 = get.PropThree(obj)           
            P3 = obj.PropOne + obj.PropTwo;
        end
    end
    methods (Static)
        % A static method is a function in a class
        % that does not depend on the instance of the class.
        % It only uses external input arguments (and maybe
        % constant properties). It is therefore very
        % similar to a 'normal' Matlab function.
        function Output = FunctionTwo(InputOne,InputTwo)
            % A static method that just multiplies two inputs
            Output = InputOne * InputTwo;
        end
    end
end
