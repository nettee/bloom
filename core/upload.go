package core

import (
	"fmt"
	"github.com/nettee/bloom/model"
	"log"
	"os"
	"os/exec"
	"path"
)

var user = os.Getenv("BLOOM_USER")
var host = os.Getenv("BLOOM_HOST")
var baseDir = os.Getenv("BLOOM_BASE_DIR")


func execCommand(cmd string) error {
	fmt.Println(cmd)
	command := exec.Command("sh", "-c", cmd)
	if err := command.Run(); err != nil {
		return err
	}
	return nil
}


func UploadImages(article model.Article) error {
	name := article.Meta().Base.Name
	log.Println(name)

	imagePath := article.ImagePath()
	imagePathStar := path.Join(imagePath, "*")
	log.Println(imagePathStar)
	targetDir := path.Join(baseDir, name)
	commands := []string {
		fmt.Sprintf("ssh %s@%s mkdir -p %s", user, host, targetDir),
		fmt.Sprintf("scp -r %s %s@%s:%s", imagePathStar, user, host, targetDir),
	}

	for _, command := range commands {
		err := execCommand(command)
		if err != nil {
			return err
		}
	}

	return nil
}
