package main

import (
	"encoding/json"
)

func calculateStringLengthAndRespond(serviceName string, inputData []byte) ([]byte, error) {
	strData := string(inputData)
	responseData := struct {
		ServiceName string `json:"service_name"`
		Length      int    `json:"length"`
	}{
		ServiceName: serviceName,
		Length:      len(strData),
	}

	jsonResponse, err := json.Marshal(responseData)
	if err != nil {
		return nil, err
	}
	return jsonResponse, nil
}
