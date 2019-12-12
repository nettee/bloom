package main

import (
	"fmt"
	"io/ioutil"
	"log"
	"strings"
)

func listItems() error {
	items, err := ioutil.ReadDir(bloomStore)
	if err != nil {
		log.Fatal(err)
	}

	count := 0
	for _, item := range items {
		itemName := item.Name()
		if strings.HasPrefix(itemName, ".") {
			continue
		}
		fmt.Println(itemName)
		count += 1
	}
	fmt.Printf("%v articles(collections).\n", count)

	return nil
}

