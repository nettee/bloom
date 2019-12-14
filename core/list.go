package core

import (
	"fmt"
	"github.com/nettee/bloom/config"
	"io/ioutil"
	"strings"
)

func ListItems() error {
	items, err := ioutil.ReadDir(config.BloomStore)
	if err != nil {
		return err
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

