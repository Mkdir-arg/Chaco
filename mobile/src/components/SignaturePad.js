import React, { useRef, useState, forwardRef, useImperativeHandle } from 'react';
import { View, StyleSheet, PanResponder } from 'react-native';
import Svg, { Path } from 'react-native-svg';

const SignaturePad = forwardRef(({ onEnd }, ref) => {
    const [paths, setPaths] = useState([]);
    const [currentPath, setCurrentPath] = useState('');
    const pathsRef = useRef([]);
    const currentPathRef = useRef('');

    useImperativeHandle(ref, () => ({
        clear: () => {
            setPaths([]);
            setCurrentPath('');
            pathsRef.current = [];
            currentPathRef.current = '';
            if (onEnd) {
                onEnd([]);
            }
        },
        getPaths: () => pathsRef.current
    }));

    const panResponder = useRef(
        PanResponder.create({
            onStartShouldSetPanResponder: () => true,
            onMoveShouldSetPanResponder: () => true,
            onPanResponderGrant: (evt) => {
                const { locationX, locationY } = evt.nativeEvent;
                const initialPath = `M${locationX},${locationY}`;
                currentPathRef.current = initialPath;
                setCurrentPath(initialPath);
            },
            onPanResponderMove: (evt) => {
                const { locationX, locationY } = evt.nativeEvent;
                const updatedPath = `${currentPathRef.current} L${locationX},${locationY}`;
                currentPathRef.current = updatedPath;
                setCurrentPath(updatedPath);
            },
            onPanResponderRelease: () => {
                const completedPath = currentPathRef.current;
                if (completedPath) {
                    const newPaths = [...pathsRef.current, completedPath];
                    pathsRef.current = newPaths;
                    setPaths(newPaths);
                    setCurrentPath('');
                    currentPathRef.current = '';
                    if (onEnd) {
                        onEnd(newPaths);
                    }
                }
            },
        })
    ).current;

    return (
        <View style={styles.container}>
            <View style={styles.canvas} {...panResponder.panHandlers}>
                <Svg height="100%" width="100%">
                    {paths.map((path, index) => (
                        <Path
                            key={index}
                            d={path}
                            stroke="#000"
                            strokeWidth={3}
                            fill="none"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                        />
                    ))}
                    {currentPath && (
                        <Path
                            d={currentPath}
                            stroke="#000"
                            strokeWidth={3}
                            fill="none"
                            strokeLinecap="round"
                            strokeLinejoin="round"
                        />
                    )}
                </Svg>
            </View>
        </View>
    );
});

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#FFF',
        padding: 5,
    },
    canvas: {
        flex: 1,
        borderWidth: 2,
        borderColor: '#DDD',
        borderRadius: 16,
        backgroundColor: '#FAFAFA',
        borderStyle: 'dashed',
    },
});

export default SignaturePad;
