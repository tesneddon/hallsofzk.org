module.exports = function(grunt) {
  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),

    clean: {
      all : [ './css', './fonts', './img', './js' ],
      site : [ '_site/' ]
    }, /* clean */

    copy: {
      'font-awesome': {
        files: [{
          expand: true, 
          cwd: 'bower_components/font-awesome/fonts',
          src: ['**'],
          dest: './fonts'
        }]
      }, /* font-awesome */
      bootstrap: {
        files: [{
          expand: true, 
          cwd: 'bower_components/bootstrap/fonts',
          src: ['**'],
          dest: './fonts'
        }]
      }, /* bootstrap */
      images: {
        files: [{
          expand: true, 
          cwd: '_img',
          src: ['**'],
          dest: './img'
        }]
      } /* images */
    }, /* copy */

    less: {
      local: {
        options: {
          paths: [ 'bower_components/bootstrap/less',
                   'bower_components/font-awesome/less' ],
          yuicompress: true
        },
        files: {
          './css/styles.css': '_less/styles.less'
        }
      }
    }, /* less */

    jekyll: {
      build: {
        options: {
          server: false
        }
      },
      serve: {
        options: {
          skip_initial_build: true,
          serve: true,
          baseurl: ""
        }
      }
    }, /* jekyll */

    uglify: {
      options: {
        banner: '/*! <%= pkg.name %> */\n'
      },
      bootstrap: {
        files: {
          'js/bootstrap.min.js':
            'bower_components/bootstrap/dist/js/bootstrap.js'
        }
      }, /* bootstrap */
      jquery: {
        files: {
          'js/jquery.min.js': 'bower_components/jquery/dist/jquery.js'
        }
      }, /* jquery */
      'jquery-easing': {
        files: {
          'js/jquery.easing.min.js':
                'bower_components/jquery-easing/jquery.easing.js'
        }
      }, /* jquery-easing */
      'jquery-ui': {
        files: {
          'js/jquery.ui.min.js': 'bower_components/jquery-ui/ui/jquery-ui.js'
        }
      }, /* jquery-ui */
      local: {
        files: [{
          expand: true,
          cwd: './_js',
          src: '**/*.js',
          dest: './js'
        }]
      } /* local */
    }, /* uglify */
    humans_txt: {
      options: {
        tab: "  ",
        commentStyle: "c",
        includeUpdateIn: "site",
        content: grunt.file.readJSON("humans.json")
      },
      files: {
        dest: "build/humans.txt"
      }
    }, /* humans_txt */
    'ftp-deploy': {
      build: {
        auth: {
          host: 'ftp.endlesssoftware.com.au'
        },
        forceVerbose: true,
        src: 'site/',
        dest: '/web/<%= pkg.name %>'
      }
    } /* ftp-deploy */
  });

  grunt.loadNpmTasks('grunt-contrib-clean');
  grunt.loadNpmTasks('grunt-contrib-copy');
  grunt.loadNpmTasks('grunt-contrib-less');
  grunt.loadNpmTasks('grunt-contrib-uglify');
  grunt.loadNpmTasks('grunt-jekyll');
  grunt.loadNpmTasks('grunt-humans-txt');
  grunt.loadNpmTasks('grunt-jekyll');
  grunt.loadNpmTasks('grunt-ftp-deploy');

  /*
  ** Command line tasks
  */
  grunt.registerTask('build',     [ 'copy', 'uglify', 'less', 'jekyll:build' ]);
  grunt.registerTask('default',   [ 'build' ]);
  grunt.registerTask('serve',     [ 'jekyll:serve' ]);
  grunt.registerTask('deploy',    [ 'ftp-deploy' ]);
};
